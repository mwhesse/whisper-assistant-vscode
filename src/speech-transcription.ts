import * as vscode from 'vscode';
import { exec, ChildProcess, spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import OpenAI from 'openai';

const execAsync = promisify(exec);

interface Segment {
  id: number;
  seek: number;
  start: number;
  end: number;
  text: string;
  tokens: number[];
  temperature: number;
}

export interface Transcription {
  text: string;
  segments: Segment[];
  language: string;
}

export type WhisperModel = 'whisper-1' | 'whisper-large-v3-turbo';

type ApiProvider = 'localhost' | 'openai' | 'groq';

interface ApiConfig {
  baseURL: string;
  apiKey: string;
}

const PROVIDER_MODELS: Record<ApiProvider, WhisperModel> = {
  openai: 'whisper-1',
  groq: 'whisper-large-v3-turbo',
  localhost: 'whisper-1', // default to OpenAI model for localhost
};

class SpeechTranscription {
  private fileName: string = 'recording';
  private recordingProcess: ChildProcess | null = null;
  private tempDir: string;

  constructor(
    private storagePath: string,
    private outputChannel: vscode.OutputChannel,
  ) {
    // Create a temp directory within the storage path
    this.tempDir = path.join(this.storagePath, 'temp');
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
  }

  private getApiConfig(): ApiConfig {
    const config = vscode.workspace.getConfiguration('whisperx-assistant');
    const provider = config.get<ApiProvider>('apiProvider') || 'localhost';

    const apiKey = config.get<string>('apiKey');
    if (!apiKey) {
      vscode.window.showErrorMessage(
        `WhisperX Assistant: API key not configured for ${provider}. Please set the API key in settings.`,
      );
      throw new Error(`API key not configured for ${provider}`);
    }

    const baseURLs: Record<ApiProvider, string> = {
      localhost:
        (config.get('customEndpoint') || 'http://localhost:4444') + '/v1',
      openai: 'https://api.openai.com/v1',
      groq: 'https://api.groq.com/openai/v1',
    };

    return {
      baseURL: baseURLs[provider],
      apiKey,
    };
  }

  async checkIfInstalled(): Promise<boolean> {
    try {
      const config = vscode.workspace.getConfiguration('whisperx-assistant');
      const soxPath = config.get<string>('soxExecutablePath') || 'sox';
      
      // Use a more reliable check for Windows
      if (process.platform === 'win32') {
        // Try to run sox with --version which is more reliable than --help on Windows
        await execAsync(`"${soxPath}" --version`);
      } else {
        await execAsync(`"${soxPath}" --help`);
      }
      return true;
    } catch (error) {
      this.outputChannel.appendLine(
        `WhisperX Assistant: Sox check failed: ${error}`,
      );
      return false;
    }
  }

  getOutputDir(): string {
    return this.storagePath;
  }

  startRecording(): boolean {
    try {
      // Ensure temp directory exists
      if (!fs.existsSync(this.tempDir)) {
        fs.mkdirSync(this.tempDir, { recursive: true });
      }

      const outputPath = path.join(this.tempDir, `${this.fileName}.wav`);

      // Check for custom recording command first
      const config = vscode.workspace.getConfiguration('whisperx-assistant');
      const customCommand = config.get<string>('customRecordingCommand') || '';

      if (customCommand.trim()) {
        this.outputChannel.appendLine(
          'WhisperX Assistant: Using custom recording command',
        );
        return this.startCustomRecording(outputPath, customCommand);
      } else {
        this.outputChannel.appendLine(
          'WhisperX Assistant: Using sox for recording (default)',
        );
        this.startSoxRecording(outputPath);
        return true;
      }
    } catch (error) {
      this.outputChannel.appendLine(`WhisperX Assistant: error: ${error}`);
      return false;
    }
  }

  private startCustomRecording(
    outputPath: string,
    customCommand: string,
  ): boolean {
    // Validate that the command contains the required placeholder
    if (!customCommand.includes('$AUDIO_FILE')) {
      vscode.window.showErrorMessage(
        'WhisperX Assistant: Custom recording command must include $AUDIO_FILE placeholder. Example: ffmpeg -f avfoundation -i :1 -ac 1 -ar 16000 -sample_fmt s16 $AUDIO_FILE',
      );
      return false; // Return false to indicate failure
    }

    // Replace the placeholder with the actual output path (properly quoted)
    const command = customCommand.replace(/\$AUDIO_FILE/g, `"${outputPath}"`);

    this.outputChannel.appendLine(
      `WhisperX Assistant: Executing custom command: ${command}`,
    );

    // Use platform-appropriate shell execution
    this.recordingProcess = this.spawnWithShell(command);
    this.setupProcessHandlers();
    return true; // Return true to indicate success
  }

  private spawnWithShell(command: string): ChildProcess {
    const platform = process.platform;

    switch (platform) {
      case 'win32':
        // Use cmd.exe on Windows
        return spawn('cmd', ['/c', command]);

      case 'darwin':
      case 'linux':
      default:
        // Use sh on Unix-like systems (macOS, Linux, etc.)
        return spawn('sh', ['-c', command]);
    }
  }

  private startSoxRecording(outputPath: string): void {
    try {
      const config = vscode.workspace.getConfiguration('whisperx-assistant');
      const soxPath = config.get<string>('soxExecutablePath') || 'sox';
      
      this.recordingProcess = spawn(soxPath, [
        '-d',
        '-b',
        '16',
        '-e',
        'signed',
        '-c',
        '1',
        '-r',
        '16k',
        outputPath,
      ]);
      this.setupProcessHandlers();
    } catch (error) {
      this.outputChannel.appendLine(
        `WhisperX Assistant: Error starting sox recording: ${error}`,
      );
      vscode.window.showErrorMessage(
        'WhisperX Assistant: Failed to start sox recording. Please ensure sox is installed and the path is correct in settings.',
      );
      throw error; // Re-throw so startRecording() can return false
    }
  }

  private setupProcessHandlers(): void {
    if (this.recordingProcess) {
      // Only show initial configuration
      let initialConfigShown = false;

      this.recordingProcess.stderr?.on('data', (data) => {
        const message = data.toString();
        // Only show the initial configuration message
        if (!initialConfigShown && message.includes('Input File')) {
          this.outputChannel.appendLine(
            `WhisperX Assistant: Configuration: ${message.trim()}`,
          );
          initialConfigShown = true;
        }
      });

      this.recordingProcess.stdout?.on('data', (data) => {
        this.outputChannel.appendLine(`WhisperX Assistant: stdout: ${data}`);
      });

      this.recordingProcess.on('close', (code) => {
        if (code !== 0) {
          this.outputChannel.appendLine(
            `WhisperX Assistant: Recording process exited with code ${code}`,
          );
        }
      });
    }
  }

  async stopRecording(): Promise<void> {
    if (!this.recordingProcess) {
      this.outputChannel.appendLine(
        'WhisperX Assistant: No recording process found',
      );
      return;
    }

    this.outputChannel.appendLine(
      'WhisperX Assistant: Stopping recording gracefully',
    );

    // Try graceful shutdown first with SIGINT (Ctrl+C equivalent)
    this.recordingProcess.kill('SIGINT');

    // Wait for graceful shutdown with longer timeout for file handle release
    const gracefulShutdown = new Promise<void>((resolve) => {
      const timeout = setTimeout(() => {
        resolve();
      }, 5000); // Increased to 5 second timeout for better file handle release

      this.recordingProcess!.on('exit', () => {
        clearTimeout(timeout);
        resolve();
      });
    });

    await gracefulShutdown;

    // If process is still running, force kill it
    if (this.recordingProcess && !this.recordingProcess.killed) {
      this.outputChannel.appendLine(
        'WhisperX Assistant: Force stopping recording process',
      );
      this.recordingProcess.kill('SIGKILL');
      
      // Additional wait after force kill to ensure file handle release
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    this.recordingProcess = null;
    
    // Additional file handle release wait specifically for Windows sox.exe
    if (process.platform === 'win32') {
      this.outputChannel.appendLine(
        'WhisperX Assistant: Waiting for Windows file handle release',
      );
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  async transcribeRecording(): Promise<Transcription | undefined> {
    const config = vscode.workspace.getConfiguration('whisperx-assistant');
    const provider = config.get<ApiProvider>('apiProvider') || 'localhost';

    let apiConfig: ApiConfig;
    try {
      apiConfig = this.getApiConfig();
    } catch (error) {
      // getApiConfig already shows a user error message, just return
      return undefined;
    }

    try {
      this.outputChannel.appendLine(
        `WhisperX Assistant: Transcribing recording using ${provider} API`,
      );

      const audioFilePath = path.join(this.tempDir, `${this.fileName}.wav`);
      
      // Verify file exists and is accessible before creating stream
      if (!fs.existsSync(audioFilePath)) {
        throw new Error('Recording file not found');
      }

      // Get the configured model or fall back to provider default
      const configuredModel = config.get<string | null>('model');
      const model = configuredModel ?? PROVIDER_MODELS[provider];

      this.outputChannel.appendLine(
        `WhisperX Assistant: Using model ${model} for ${provider}`,
      );

      const openai = new OpenAI({
        baseURL: apiConfig.baseURL,
        apiKey: apiConfig.apiKey,
        maxRetries: 0,
        timeout: 30 * 1000,
      });

      if (!openai) {
        vscode.window.showErrorMessage(
          'WhisperX Assistant: Failed to initialize OpenAI client. Please check your API configuration.',
        );
        return undefined;
      }

      // Create and properly manage the file stream
      const audioFile = fs.createReadStream(audioFilePath);
      
      let transcription;
      try {
        transcription = await openai.audio.transcriptions.create({
          file: audioFile,
          model: model,
          language: 'en',
          // eslint-disable-next-line @typescript-eslint/naming-convention
          response_format: 'verbose_json',
        });
      } finally {
        // Ensure the stream is properly closed to release file handle
        if (audioFile && !audioFile.destroyed) {
          audioFile.destroy();
        }
        
        // Additional wait for Windows to ensure file handle is fully released
        if (process.platform === 'win32') {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }

      // Convert response to our Transcription interface
      const result: Transcription = {
        text: transcription.text,
        segments:
          transcription.segments?.map((seg) => ({
            id: seg.id,
            seek: 0,
            start: seg.start,
            end: seg.end,
            text: seg.text,
            tokens: [],
            temperature: 0,
          })) ?? [],
        language: transcription.language,
      };

      // Save transcription to storage path
      await fs.promises.writeFile(
        path.join(this.tempDir, `${this.fileName}.json`),
        JSON.stringify(result, null, 2),
      );

      this.outputChannel.appendLine(
        `WhisperX Assistant: Transcription: ${result.text}`,
      );

      if (result?.text?.length === 0) {
        return undefined;
      }

      return result;
    } catch (error) {
      // Log the error to output channel
      this.outputChannel.appendLine(
        `WhisperX Assistant: error: ${error} (apiConfig.baseURL: ${apiConfig.baseURL})`,
      );

      if (provider === 'localhost') {
        vscode.window.showErrorMessage(
          'WhisperX Assistant: Ensure local WhisperX server is running.',
        );
      } else if (error instanceof Error) {
        // Format the error message to be more user-friendly
        const errorMessage = error.message
          .replace(/\bError\b/i, '') // Remove redundant "Error" word
          .trim();

        vscode.window.showErrorMessage(`WhisperX Assistant: ${errorMessage}`);
      }

      return undefined;
    }
  }

  async deleteFiles(): Promise<void> {
    try {
      const wavFile = path.join(this.tempDir, `${this.fileName}.wav`);
      const jsonFile = path.join(this.tempDir, `${this.fileName}.json`);

      // Wait a bit more on Windows to ensure file handles are released
      if (process.platform === 'win32') {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Try to delete files with retry logic for Windows file handle issues
      const deleteWithRetry = async (filePath: string, maxRetries: number = 3): Promise<void> => {
        for (let i = 0; i < maxRetries; i++) {
          try {
            if (fs.existsSync(filePath)) {
              fs.unlinkSync(filePath);
              return;
            }
          } catch (error) {
            if (i === maxRetries - 1) {
              throw error;
            }
            // Wait before retry, especially important on Windows
            await new Promise(resolve => setTimeout(resolve, 500 * (i + 1)));
          }
        }
      };

      await deleteWithRetry(wavFile);
      await deleteWithRetry(jsonFile);
    } catch (error) {
      this.outputChannel.appendLine(
        `WhisperX Assistant: Error deleting files: ${error}`,
      );
    }
  }

  // Add method to ensure file handles are released before operations
  private async ensureFileHandleReleased(filePath: string): Promise<void> {
    if (process.platform === 'win32') {
      // On Windows, check if file is accessible (not locked)
      let attempts = 0;
      const maxAttempts = 10;
      
      while (attempts < maxAttempts) {
        try {
          // Try to open the file in read mode to check if it's locked
          const fd = fs.openSync(filePath, 'r');
          fs.closeSync(fd);
          return; // File is accessible, handle is released
        } catch (error) {
          attempts++;
          if (attempts >= maxAttempts) {
            this.outputChannel.appendLine(
              `WhisperX Assistant: Warning - File may still be locked: ${filePath}`,
            );
            return;
          }
          // Wait before next attempt
          await new Promise(resolve => setTimeout(resolve, 200));
        }
      }
    }
  }

  // Add cleanup method for extension deactivation
  cleanup(): void {
    try {
      if (fs.existsSync(this.tempDir)) {
        fs.rmSync(this.tempDir, { recursive: true, force: true });
      }
    } catch (error) {
      this.outputChannel.appendLine(
        `WhisperX Assistant: Error cleaning up: ${error}`,
      );
    }
  }
}

export default SpeechTranscription;
