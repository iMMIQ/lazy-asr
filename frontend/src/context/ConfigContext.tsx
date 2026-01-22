import React, { createContext, useContext, useReducer, useCallback, type ReactNode } from 'react';
import {
  DEFAULT_OUTPUT_FORMATS,
  DEFAULT_MIN_SPEECH_DURATION,
  DEFAULT_MIN_SILENCE_DURATION
} from '../constants/config';
import type { ConfigState, ConfigActions, ConfigContextValue, OutputFormat, ASRPlugin, LanguageCode } from '../types';

// Initial state
const initialState: ConfigState = {
  // ASR Configuration
  asrMethod: '',
  availablePlugins: [],
  asrLanguage: 'auto',
  asrApiUrl: '',
  asrApiKey: '',
  asrModel: '',

  // VAD Configuration
  outputFormats: DEFAULT_OUTPUT_FORMATS,
  minSpeechDuration: DEFAULT_MIN_SPEECH_DURATION,
  minSilenceDuration: DEFAULT_MIN_SILENCE_DURATION,

  // Path Scanner specific
  maxFiles: 100,
  recursive: true,

  // UI State
  isProcessing: false
};

// Action types
const ActionTypes = {
  SET_ASR_METHOD: 'SET_ASR_METHOD',
  SET_AVAILABLE_PLUGINS: 'SET_AVAILABLE_PLUGINS',
  SET_ASR_LANGUAGE: 'SET_ASR_LANGUAGE',
  SET_ASR_API_URL: 'SET_ASR_API_URL',
  SET_ASR_API_KEY: 'SET_ASR_API_KEY',
  SET_ASR_MODEL: 'SET_ASR_MODEL',
  TOGGLE_OUTPUT_FORMAT: 'TOGGLE_OUTPUT_FORMAT',
  SET_MIN_SPEECH_DURATION: 'SET_MIN_SPEECH_DURATION',
  SET_MIN_SILENCE_DURATION: 'SET_MIN_SILENCE_DURATION',
  SET_MAX_FILES: 'SET_MAX_FILES',
  SET_RECURSIVE: 'SET_RECURSIVE',
  SET_PROCESSING: 'SET_PROCESSING',
  RESET_CONFIG: 'RESET_CONFIG'
} as const;

type ConfigAction =
  | { type: typeof ActionTypes.SET_ASR_METHOD; payload: string }
  | { type: typeof ActionTypes.SET_AVAILABLE_PLUGINS; payload: ASRPlugin[] }
  | { type: typeof ActionTypes.SET_ASR_LANGUAGE; payload: LanguageCode }
  | { type: typeof ActionTypes.SET_ASR_API_URL; payload: string }
  | { type: typeof ActionTypes.SET_ASR_API_KEY; payload: string }
  | { type: typeof ActionTypes.SET_ASR_MODEL; payload: string }
  | { type: typeof ActionTypes.TOGGLE_OUTPUT_FORMAT; payload: OutputFormat }
  | { type: typeof ActionTypes.SET_MIN_SPEECH_DURATION; payload: number }
  | { type: typeof ActionTypes.SET_MIN_SILENCE_DURATION; payload: number }
  | { type: typeof ActionTypes.SET_MAX_FILES; payload: number }
  | { type: typeof ActionTypes.SET_RECURSIVE; payload: boolean }
  | { type: typeof ActionTypes.SET_PROCESSING; payload: boolean }
  | { type: typeof ActionTypes.RESET_CONFIG };

// Reducer
function configReducer(state: ConfigState, action: ConfigAction): ConfigState {
  switch (action.type) {
    case ActionTypes.SET_ASR_METHOD:
      return { ...state, asrMethod: action.payload };

    case ActionTypes.SET_AVAILABLE_PLUGINS:
      return { ...state, availablePlugins: action.payload };

    case ActionTypes.SET_ASR_LANGUAGE:
      return { ...state, asrLanguage: action.payload };

    case ActionTypes.SET_ASR_API_URL:
      return { ...state, asrApiUrl: action.payload };

    case ActionTypes.SET_ASR_API_KEY:
      return { ...state, asrApiKey: action.payload };

    case ActionTypes.SET_ASR_MODEL:
      return { ...state, asrModel: action.payload };

    case ActionTypes.TOGGLE_OUTPUT_FORMAT:
      return {
        ...state,
        outputFormats: state.outputFormats.includes(action.payload)
          ? state.outputFormats.filter(f => f !== action.payload)
          : [...state.outputFormats, action.payload]
      };

    case ActionTypes.SET_MIN_SPEECH_DURATION:
      return { ...state, minSpeechDuration: action.payload };

    case ActionTypes.SET_MIN_SILENCE_DURATION:
      return { ...state, minSilenceDuration: action.payload };

    case ActionTypes.SET_MAX_FILES:
      return { ...state, maxFiles: action.payload };

    case ActionTypes.SET_RECURSIVE:
      return { ...state, recursive: action.payload };

    case ActionTypes.SET_PROCESSING:
      return { ...state, isProcessing: action.payload };

    case ActionTypes.RESET_CONFIG:
      return {
        ...initialState,
        asrMethod: state.asrMethod,
        availablePlugins: state.availablePlugins
      };

    default:
      return state;
  }
}

// Create Context
const ConfigContext = createContext<ConfigContextValue | undefined>(undefined);

// Provider Component
interface ConfigProviderProps {
  children: ReactNode;
}

export function ConfigProvider({ children }: ConfigProviderProps) {
  const [state, dispatch] = useReducer(configReducer, initialState);

  // Action creators
  const setAsrMethod = useCallback((method: string) => {
    dispatch({ type: ActionTypes.SET_ASR_METHOD, payload: method });
  }, []);

  const setAvailablePlugins = useCallback((plugins: ASRPlugin[]) => {
    dispatch({ type: ActionTypes.SET_AVAILABLE_PLUGINS, payload: plugins });
  }, []);

  const setAsrLanguage = useCallback((language: LanguageCode) => {
    dispatch({ type: ActionTypes.SET_ASR_LANGUAGE, payload: language });
  }, []);

  const setAsrApiUrl = useCallback((url: string) => {
    dispatch({ type: ActionTypes.SET_ASR_API_URL, payload: url });
  }, []);

  const setAsrApiKey = useCallback((key: string) => {
    dispatch({ type: ActionTypes.SET_ASR_API_KEY, payload: key });
  }, []);

  const setAsrModel = useCallback((model: string) => {
    dispatch({ type: ActionTypes.SET_ASR_MODEL, payload: model });
  }, []);

  const toggleOutputFormat = useCallback((format: OutputFormat) => {
    dispatch({ type: ActionTypes.TOGGLE_OUTPUT_FORMAT, payload: format });
  }, []);

  const setMinSpeechDuration = useCallback((duration: number) => {
    dispatch({ type: ActionTypes.SET_MIN_SPEECH_DURATION, payload: duration });
  }, []);

  const setMinSilenceDuration = useCallback((duration: number) => {
    dispatch({ type: ActionTypes.SET_MIN_SILENCE_DURATION, payload: duration });
  }, []);

  const setMaxFiles = useCallback((max: number) => {
    dispatch({ type: ActionTypes.SET_MAX_FILES, payload: max });
  }, []);

  const setRecursive = useCallback((recursive: boolean) => {
    dispatch({ type: ActionTypes.SET_RECURSIVE, payload: recursive });
  }, []);

  const setProcessing = useCallback((isProcessing: boolean) => {
    dispatch({ type: ActionTypes.SET_PROCESSING, payload: isProcessing });
  }, []);

  const resetConfig = useCallback(() => {
    dispatch({ type: ActionTypes.RESET_CONFIG });
  }, []);

  const value: ConfigContextValue = {
    state,
    actions: {
      setAsrMethod,
      setAvailablePlugins,
      setAsrLanguage,
      setAsrApiUrl,
      setAsrApiKey,
      setAsrModel,
      toggleOutputFormat,
      setMinSpeechDuration,
      setMinSilenceDuration,
      setMaxFiles,
      setRecursive,
      setProcessing,
      resetConfig
    }
  };

  return (
    <ConfigContext.Provider value={value}>
      {children}
    </ConfigContext.Provider>
  );
}

// Custom Hook
export function useConfig(): ConfigContextValue {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
}

export default ConfigContext;
