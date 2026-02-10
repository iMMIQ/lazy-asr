# Frontend VAD Configuration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add frontend UI for selecting VAD (Voice Activity Detection) method, supporting multiple VAD providers (silero, ten) with backend configuration.

**Architecture:** Extend existing ConfigContext/ConfigPanel pattern to support VAD providers similar to ASR plugins. Fetch providers from `/api/v1/vad/providers`, add selector in VAD config section, send `vad_method` in FormData.

**Tech Stack:** React + TypeScript, i18n (react-i18next), axios, existing ConfigContext pattern

---

## Task 1: Add VAD Provider Types

**Files:**
- Modify: `frontend/src/types/index.ts`

**Step 1: Add VAD provider types to types/index.ts**

Add these exports after line 27 (after ASRPlugin interface):

```typescript
/** VAD provider information */
export interface VADProvider {
  name: string;
  display_name: string;
  description: string;
}

/** VAD providers response */
export interface VADProvidersResponse {
  providers: VADProvider[];
  default: string;
}
```

**Step 2: Update ConfigState interface**

Add these fields to ConfigState interface (after line 22, in VAD Configuration section):

```typescript
// VAD Configuration - add these:
vadMethod: string;
availableVADProviders: VADProvider[];
```

**Step 3: Update ConfigActions interface**

Add this action to ConfigActions interface (after line 208):

```typescript
setVadMethod: (method: string) => void;
setAvailableVADProviders: (providers: VADProvider[]) => void;
```

**Step 4: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat(types): add VAD provider types"
```

---

## Task 2: Add VAD API Service

**Files:**
- Modify: `frontend/src/services/api.ts`

**Step 1: Add VAD providers fetch function**

Add this function after the fetchPlugins function (after line 51):

```typescript
/**
 * Fetch available VAD providers from backend
 */
export async function fetchVADProviders(): Promise<VADProvidersResponse> {
  try {
    const response = await apiClient.get<VADProvidersResponse>('/vad/providers');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch VAD providers:', error);
    throw new Error(getErrorMessage(error));
  }
}
```

**Step 2: Add VADProvidersResponse import**

Add `VADProvidersResponse` to the import statement at line 2:

```typescript
import type {
  ASRPlugin,
  ApiErrorResponse,
  ProcessResult,
  ScanRequest,
  ScanResult,
  ScanStatusResponse,
  DirectoryBrowseResult,
  PathInfo,
  MonitorConfig,
  MonitorListResponse,
  MonitorServiceStatus,
  DatabaseStatus,
  VADProvidersResponse
} from '../types';
```

**Step 3: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat(api): add fetchVADProviders function"
```

---

## Task 3: Update ConfigContext with VAD State

**Files:**
- Modify: `frontend/src/context/ConfigContext.tsx`

**Step 1: Add imports**

Update the import at line 7 to include new types:

```typescript
import type { ConfigState, ConfigContextValue, OutputFormat, ASRPlugin, LanguageCode, VADProvider } from '../types';
```

**Step 2: Update initialState**

Add these fields to initialState (after line 22, in VAD Configuration section):

```typescript
// VAD Configuration
vadMethod: '',
availableVADProviders: [],
outputFormats: DEFAULT_OUTPUT_FORMATS,
minSpeechDuration: DEFAULT_MIN_SPEECH_DURATION,
minSilenceDuration: DEFAULT_MIN_SILENCE_DURATION,
```

**Step 3: Add action types**

Add these to ActionTypes (after line 42):

```typescript
  SET_VAD_METHOD: 'SET_VAD_METHOD',
  SET_AVAILABLE_VAD_PROVIDERS: 'SET_AVAILABLE_VAD_PROVIDERS',
```

**Step 4: Add action types to union**

Add these types to ConfigAction union (after line 56):

```typescript
  | { type: typeof ActionTypes.SET_VAD_METHOD; payload: string }
  | { type: typeof ActionTypes.SET_AVAILABLE_VAD_PROVIDERS; payload: VADProvider[] }
```

**Step 5: Add reducer cases**

Add these cases to configReducer (after line 83, before the TOGGLE_OUTPUT_FORMAT case):

```typescript
    case ActionTypes.SET_VAD_METHOD:
      return { ...state, vadMethod: action.payload };

    case ActionTypes.SET_AVAILABLE_VAD_PROVIDERS:
      return { ...state, availableVADProviders: action.payload };
```

**Step 6: Add action creators**

Add these functions after setAsrModel (after line 158):

```typescript
  const setVadMethod = useCallback((method: string) => {
    dispatch({ type: ActionTypes.SET_VAD_METHOD, payload: method });
  }, []);

  const setAvailableVADProviders = useCallback((providers: VADProvider[]) => {
    dispatch({ type: ActionTypes.SET_AVAILABLE_VAD_PROVIDERS, payload: providers });
  }, []);
```

**Step 7: Export actions**

Add these to the value object (after line 199):

```typescript
      setVadMethod,
      setAvailableVADProviders,
```

**Step 8: Commit**

```bash
git add frontend/src/context/ConfigContext.tsx
git commit -m "feat(context): add VAD method state to ConfigContext"
```

---

## Task 4: Update buildFormData to Include vad_method

**Files:**
- Modify: `frontend/src/hooks/useASRProcessing.ts`

**Step 1: Add vadMethod to ASRProcessingOptions interface**

Add this field to the interface (after line 18):

```typescript
  vadMethod: string;
```

**Step 2: Add vadMethod to FormData**

Add these lines in buildFormData function (after line 208, after `output_mode` append):

```typescript
    // Add VAD method
    if (vadMethod) {
      formData.append('vad_method', vadMethod);
    }
```

**Step 3: Commit**

```bash
git add frontend/src/hooks/useASRProcessing.ts
git commit -m "feat(hook): add vad_method to FormData builder"
```

---

## Task 5: Update ConfigPanel Component

**Files:**
- Modify: `frontend/src/components/ConfigPanel.tsx`

**Step 1: Add props to ConfigPanelProps interface**

Add these props (after line 27):

```typescript
  vadMethod?: string;
  availableVADProviders?: { name: string; display_name: string; description: string }[];
```

**Step 2: Add handler to ConfigPanelHandlers interface**

Add this handler (after line 13):

```typescript
  onVadMethodChange?: (method: string) => void;
```

**Step 3: Add props to function parameters**

Add these to the destructured parameters (after line 64):

```typescript
  vadMethod = '',
  availableVADProviders = [],
```

**Step 4: Add handler parameter**

Add this to destructured event handlers (after line 69):

```typescript
  onVadMethodChange,
```

**Step 5: Add VAD method selector to JSX**

Add this select element at line 238 (right before the VAD Configuration section):

```typescript
      {/* VAD Method Selection */}
      {showVadConfig && availableVADProviders.length > 0 && (
        <div className="form-group">
          <label htmlFor="vadMethod">{t('form.vadMethod')}</label>
          <select
            id="vadMethod"
            value={vadMethod || ''}
            onChange={(e) => onVadMethodChange && onVadMethodChange(e.target.value)}
            disabled={isProcessing}
          >
            {availableVADProviders.map((provider) => (
              <option key={provider.name} value={provider.name}>
                {provider.name}
              </option>
            ))}
          </select>
          <small>{t('form.vadMethodDescription')}</small>
        </div>
      )}
```

**Step 6: Commit**

```bash
git add frontend/src/components/ConfigPanel.tsx
git commit -m "feat(config-panel): add VAD method selector"
```

---

## Task 6: Add i18n Translations

**Files:**
- Modify: `frontend/src/locales/zh.json`
- Modify: `frontend/src/locales/en.json`

**Step 1: Add Chinese translations**

Add these lines to zh.json (after line 16, in form section):

```json
    "vadMethod": "VAD方法:",
    "vadMethodDescription": "选择语音活动检测方法"
```

**Step 2: Add English translations**

Add these lines to en.json (after line 16, in form section):

```json
    "vadMethod": "VAD Method:",
    "vadMethodDescription": "Select voice activity detection method"
```

**Step 3: Commit**

```bash
git add frontend/src/locales/zh.json frontend/src/locales/en.json
git commit -m "feat(i18n): add VAD method translations"
```

---

## Task 7: Update FileUploadTab to Use VAD Method

**Files:**
- Modify: `frontend/src/components/FileUploadTab.tsx`

**Step 1: Add VAD method to buildFormData call in handleSingleSubmit**

Update the formData building (around line 52-65) to include vadMethod:

```typescript
      const formData = buildFormData({
        audioFiles,
        asrMethod: state.asrMethod,
        outputFormats: state.outputFormats,
        showAdvancedOptions: true,
        outputMode: 'task',
        minSpeechDuration: state.minSpeechDuration,
        minSilenceDuration: state.minSilenceDuration,
        asrApiUrl: state.asrApiUrl,
        asrApiKey: state.asrApiKey,
        asrModel: state.asrModel,
        asrLanguage: state.asrLanguage,
        vadMethod: state.vadMethod,
        isMultiple: false
      });
```

**Step 2: Add VAD method to buildFormData call in handleMultipleSubmit**

Update the formData building (around line 83-96) to include vadMethod:

```typescript
      const formData = buildFormData({
        audioFiles,
        asrMethod: state.asrMethod,
        outputFormats: state.outputFormats,
        showAdvancedOptions: true,
        outputMode: 'task',
        minSpeechDuration: state.minSpeechDuration,
        minSilenceDuration: state.minSilenceDuration,
        asrApiUrl: state.asrApiUrl,
        asrApiKey: state.asrApiKey,
        asrModel: state.asrModel,
        asrLanguage: state.asrLanguage,
        vadMethod: state.vadMethod,
        isMultiple: true
      });
```

**Step 3: Add VAD props to ConfigPanel**

Update ConfigPanel props (around line 114-154) to include:

```typescript
        <ConfigPanel
          asrMethod={state.asrMethod}
          availablePlugins={state.availablePlugins}
          vadMethod={state.vadMethod}
          availableVADProviders={state.availableVADProviders}
          outputFormats={state.outputFormats}
          ...
          onVadMethodChange={(method) => actions.setVadMethod(method)}
          onVadConfigChange={(field, value) => {
```

**Step 4: Commit**

```bash
git add frontend/src/components/FileUploadTab.tsx
git commit -m "feat(file-upload): pass VAD method to ConfigPanel and FormData"
```

---

## Task 8: Update PathScanner Component

**Files:**
- Modify: `frontend/src/components/PathScanner.tsx`

**Step 1: Read PathScanner to understand current implementation**

Note: This component may have similar patterns to FileUploadTab. Look for:
- ConfigPanel usage
- buildFormData or similar function
- API calls that need vad_method

**Step 2: Add VAD method selector support**

Following the same pattern as FileUploadTab:
1. Add vadMethod and availableVADProviders props to ConfigPanel
2. Add onVadMethodChange handler
3. Include vad_method in API requests

**Step 3: Commit**

```bash
git add frontend/src/components/PathScanner.tsx
git commit -m "feat(path-scanner): add VAD method configuration"
```

---

## Task 9: Update App Component to Fetch VAD Providers

**Files:**
- Modify: `frontend/src/components/App.tsx`

**Step 1: Add fetchVADProviders import**

Add to imports:

```typescript
import { fetchPlugins, fetchVADProviders } from './services/api';
```

**Step 2: Create useEffect to fetch VAD providers**

Add this effect after the plugins fetch effect:

```typescript
  // Fetch VAD providers on mount
  useEffect(() => {
    const loadVADProviders = async () => {
      try {
        const response = await fetchVADProviders();
        actions.setAvailableVADProviders(response.providers);
        // Set default VAD method from backend
        if (response.default && !state.vadMethod) {
          actions.setVadMethod(response.default);
        }
      } catch (error) {
        console.error('Failed to load VAD providers:', error);
      }
    };
    loadVADProviders();
  }, [actions]);
```

**Step 3: Commit**

```bash
git add frontend/src/components/App.tsx
git commit -m "feat(app): fetch VAD providers on mount"
```

---

## Task 10: Update Backend Default VAD Method

**Files:**
- Modify: `backend/app/core/config.py`

**Step 1: Change DEFAULT_VAD_METHOD to "ten"**

Update line 38:

```python
    DEFAULT_VAD_METHOD: str = "ten"
```

**Step 2: Commit**

```bash
git add backend/app/core/config.py
git commit -m "feat(config): change default VAD method to ten"
```

---

## Task 11: Write Tests

**Files:**
- Modify: `frontend/src/hooks/useASRProcessing.test.ts` (if exists)
- Create: `frontend/src/services/api.test.ts` (if not exists)

**Step 1: Test fetchVADProviders function**

```typescript
describe('fetchVADProviders', () => {
  it('should return VAD providers list', async () => {
    const mockProviders = {
      providers: [
        { name: 'silero', display_name: 'Silero VAD', description: 'Silero VAD' },
        { name: 'ten', display_name: 'Ten VAD', description: 'Ten VAD' }
      ],
      default: 'ten'
    };

    mockedApiClient.get.mockResolvedValue({ data: mockProviders });

    const result = await fetchVADProviders();
    expect(result).toEqual(mockProviders);
  });
});
```

**Step 2: Test buildFormData includes vad_method**

```typescript
describe('buildFormData', () => {
  it('should include vad_method in FormData', () => {
    const { buildFormData } = renderHook(() => useASRProcessing()).result.current;

    const formData = buildFormData({
      audioFiles: [new File([''], 'test.mp3')],
      asrMethod: 'local-whisper',
      outputFormats: ['srt'],
      showAdvancedOptions: true,
      minSpeechDuration: 500,
      minSilenceDuration: 500,
      asrApiUrl: '',
      asrApiKey: '',
      asrModel: '',
      asrLanguage: 'auto',
      vadMethod: 'ten',
      isMultiple: false
    });

    expect(formData.get('vad_method')).toBe('ten');
  });
});
```

**Step 3: Run tests**

```bash
cd frontend && npm test
```

**Step 4: Commit**

```bash
git add frontend/src/hooks/useASRProcessing.test.ts frontend/src/services/api.test.ts
git commit -m "test: add VAD provider tests"
```

---

## Task 12: Manual Testing

**Step 1: Start backend**

```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Step 2: Start frontend**

```bash
cd frontend
npm run dev
```

**Step 3: Test VAD providers endpoint**

```bash
curl http://localhost:8000/api/v1/vad/providers
```

Expected output:
```json
{
  "providers": [
    {"name": "silero", "display_name": "Silero VAD", "description": "..."},
    {"name": "ten", "display_name": "Ten VAD", "description": "..."}
  ],
  "default": "ten"
}
```

**Step 4: Test UI flow**

1. Open browser to http://localhost:5173
2. Verify VAD method selector appears in VAD config section
3. Verify "ten" is selected by default
4. Verify both "silero" and "ten" options are available
5. Upload a file and process
6. Verify vad_method is sent in request (check browser network tab)

**Step 5: Commit**

If tests pass:

```bash
git commit --allow-empty -m "test: manual VAD configuration testing complete"
```

---

## Task 13: Update Documentation

**Files:**
- Modify: `README.md` (if applicable)

**Step 1: Document VAD configuration**

Add section about VAD configuration in README if it documents UI features:

```markdown
### VAD Configuration

The application supports multiple Voice Activity Detection (VAD) methods:
- **Silero VAD**: Traditional neural VAD
- **Ten VAD**: Alternative VAD implementation

You can select the VAD method in the VAD Configuration section. The default is Ten VAD.
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: document VAD configuration feature"
```

---

## Summary

This plan implements frontend VAD method configuration by:

1. Adding types for VAD providers
2. Creating API service to fetch providers
3. Extending ConfigContext with VAD state
4. Adding VAD selector to ConfigPanel
5. Including vad_method in API requests
6. Setting default VAD to "ten" in backend
7. Adding i18n support
8. Testing and documentation

The implementation follows existing patterns (ASR plugin selection) for consistency.
