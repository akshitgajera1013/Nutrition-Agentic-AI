# add_voiceover.ps1
# Generates TTS voiceover for all 18 slides and merges with MP4 using ffmpeg
# Output: NutriGuide_Agentic_AI_Voiceover.mp4 (~150 seconds)

$ffmpeg  = 'C:\Users\STUDENT\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe'
$workDir = Split-Path (Resolve-Path 'NutriGuide_Agentic_AI_Video.mp4').Path
$videoIn = Join-Path $workDir 'NutriGuide_Agentic_AI_Video.mp4'
$audioOut= Join-Path $workDir 'voiceover_full.wav'
$finalOut= Join-Path $workDir 'NutriGuide_Agentic_AI_Voiceover.mp4'

Write-Host '================================================'
Write-Host '  NutriGuide Agentic AI - Voiceover Generator'
Write-Host '  Windows TTS + FFmpeg merge -> 150s MP4'
Write-Host '================================================'
Write-Host ''

# ---- Slide narration scripts (8.33 sec each, ~18 slides = 150 sec) ----
$narrations = @(
    # Slide 1 - Title
    'Welcome to NutriGuide, the Nutrition Agentic AI application. Powered by IBM Granite 3.3, this intelligent web application generates personalized nutrition plans using artificial intelligence, following ethical AI principles and HAM guidelines.',

    # Slide 2 - Project Overview
    'NutriGuide is a full-stack web application that collects your health profile and creates a complete 7-day nutrition plan. It uses IBM Granite via Watsonx dot ai, with a Python Flask backend and a responsive single-page web interface.',

    # Slide 3 - SDLC
    'The project follows all 8 phases of the Agentic AI Software Development Lifecycle: Requirements analysis, system architecture, agent design, development, guardrails implementation, testing, deployment, and continuous monitoring.',

    # Slide 4 - Architecture
    'The system architecture has three layers. The browser-based single-page application communicates with the Flask backend via REST API. The backend contains the plan agent, Q and A agent, guardrails, and disclaimer modules. IBM Granite processes all AI requests through Watsonx dot ai.',

    # Slide 5 - Features
    'NutriGuide offers 9 powerful features including IBM Granite language model integration, personalized user profiling, complete 7-day meal plans, ethical guardrails, context-aware Q and A agent, markdown file export, HAM principles, medical disclaimers, and a fully functional demo mode.',

    # Slide 6 - UI Screenshot Home
    'The web application opens with a clean two-panel layout. The left panel presents the user profile form collecting name, age, diet preference, medical history, city, and country. The right panel shows welcome cards describing the plan features. A status indicator shows whether IBM Granite is connected.',

    # Slide 7 - UI Generating
    'When you submit the form, the agent pipeline begins. Input is validated through guardrails, harmful content is checked, then IBM Granite is prompted with your full profile. The generation takes a few seconds while a loading animation is displayed.',

    # Slide 8 - Plan Output
    'The generated plan appears as beautifully formatted markdown. A meta bar shows your profile details, followed by action buttons to download, copy, or regenerate. The plan includes calorie targets, macronutrient breakdown, and a complete 7-day meal schedule.',

    # Slide 9 - MD File
    'Every nutrition plan is automatically saved as a dot md markdown file with YAML frontmatter recording the model name, timestamp, and application details. The file can be downloaded directly from the web interface via the download button.',

    # Slide 10 - Q&A Agent
    'The Ask NutriGuide tab activates the Q and A agent. You can click quick suggestion chips or type any nutrition question. IBM Granite answers in context of your profile. Each answer includes a medical disclaimer reminding you to consult a healthcare professional.',

    # Slide 11 - Guardrails
    'Ethical AI is enforced at three levels. Input guardrails validate all form data and block 25 or more harmful keywords. LLM guardrails embed HAM principles into the system prompt and sanitize all outputs. Medical disclaimers are generated for every response.',

    # Slide 12 - IBM Granite
    'IBM Granite 3.3 8 Billion Instruct is accessed via the ibm-watsonx-ai Python SDK. The model uses the instruct prompt format with a carefully engineered system prompt. Maximum 2048 tokens, temperature 0.7, with repetition penalty enabled for natural responses.',

    # Slide 13 - API Endpoints
    'The application exposes 5 REST API endpoints. GET slash serves the web app. POST slash api slash generate-plan creates the nutrition plan. POST slash api slash ask handles Q and A. GET slash api slash download-plan provides the markdown file. GET slash api slash health reports the LLM connection status.',

    # Slide 14 - Project Structure
    'The project contains 13 files including app dot py for backend logic, guardrails dot py for ethics enforcement, disclaimer dot py for medical notices, requirements dot txt for dependencies, the run dot bat launcher, README dot md documentation, and the complete frontend in templates and static folders.',

    # Slide 15 - Deployment
    'Deployment is simplified by run dot bat, a one-click Windows launcher. It automatically checks Python, creates a virtual environment, installs all dependencies, optionally configures your IBM Watsonx API key, creates the plans directory, launches Flask, and opens the browser at localhost port 5000.',

    # Slide 16 - GitHub
    'The complete project is hosted on GitHub at github dot com slash akshitgajera1013 slash Nutrition-Agentic-AI. All 13 application files, the presentation, and this video are committed to the main branch. Simply clone the repository and run the bat file to start.',

    # Slide 17 - Disclaimer
    'Every nutrition plan includes a comprehensive medical disclaimer. The disclaimer states that NutriGuide provides general nutritional information only, and is not a substitute for professional medical advice. Users with diabetes, high blood pressure, or other conditions receive enhanced safety notices.',

    # Slide 18 - Thank You
    'Thank you for watching this demonstration of NutriGuide, the Nutrition Agentic AI application. Built with IBM Granite 3.3 and Watsonx dot ai, following ethical AI and HAM principles. The full source code is available on GitHub. Always consult a qualified healthcare provider before making dietary changes.'
)

# ---- Generate TTS for each slide ----
Write-Host '[1/3] Generating TTS audio for 18 slides...'

Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

# Use Microsoft David Desktop (clear male voice)
try {
    $synth.SelectVoice('Microsoft David Desktop')
    Write-Host '      Voice: Microsoft David Desktop'
} catch {
    Write-Host '      Voice: Default system voice'
}

$synth.Rate   = -1    # Slightly slower for clarity (-10 to 10)
$synth.Volume = 100   # Max volume

# Generate individual WAV files per slide
$slideWavs = @()
for ($i = 0; $i -lt $narrations.Count; $i++) {
    $slideNum  = $i + 1
    $wavFile   = Join-Path $workDir ('slide_' + $slideNum + '_audio.wav')
    $synth.SetOutputToWaveFile($wavFile)
    $synth.Speak($narrations[$i])
    $synth.SetOutputToNull()
    $slideWavs += $wavFile
    Write-Host ('      Slide ' + $slideNum + '/18 -> ' + (Split-Path $wavFile -Leaf))
}

$synth.Dispose()
Write-Host '      All 18 slide narrations generated.'
Write-Host ''

# ---- Concatenate all WAVs using ffmpeg ----
Write-Host '[2/3] Concatenating audio tracks with FFmpeg...'

# Build ffmpeg concat filter for 18 inputs
$inputArgs = @()
foreach ($wav in $slideWavs) {
    $inputArgs += '-i'
    $inputArgs += $wav
}

# Build filter_complex string: [0][1][2]...[17]concat=n=18:v=0:a=1[outa]
$concatInputs = ''
for ($i = 0; $i -lt $slideWavs.Count; $i++) {
    $concatInputs += "[$i]"
}
$filterComplex = $concatInputs + 'concat=n=' + $slideWavs.Count + ':v=0:a=1[outa]'

$ffmpegArgs = $inputArgs + @(
    '-filter_complex', $filterComplex,
    '-map', '[outa]',
    '-ar', '44100',
    '-ac', '2',
    '-y',
    $audioOut
)

& $ffmpeg @ffmpegArgs 2>&1 | Where-Object { $_ -match 'error|Error|size=|time=' } | Select-Object -Last 5

if (Test-Path $audioOut) {
    $audioMB = [math]::Round((Get-Item $audioOut).Length/1MB, 2)
    Write-Host ('      Audio track created: ' + $audioMB + ' MB')
} else {
    Write-Host 'ERROR: Audio concatenation failed.'
    exit 1
}

Write-Host ''

# ---- Merge audio + video with ffmpeg ----
Write-Host '[3/3] Merging voiceover with video...'

& $ffmpeg -i $videoIn -i $audioOut `
    -c:v copy `
    -c:a aac -b:a 192k `
    -map '0:v:0' -map '1:a:0' `
    -shortest `
    -movflags +faststart `
    -y $finalOut 2>&1 | Where-Object { $_ -match 'error|Error|size=|time=' } | Select-Object -Last 5

# ---- Cleanup slide WAVs ----
foreach ($wav in $slideWavs) {
    Remove-Item $wav -ErrorAction SilentlyContinue
}
Remove-Item $audioOut -ErrorAction SilentlyContinue

# ---- Result ----
if (Test-Path $finalOut) {
    $mb = [math]::Round((Get-Item $finalOut).Length / 1MB, 2)
    Write-Host ''
    Write-Host '================================================'
    Write-Host '  VOICEOVER VIDEO COMPLETE!'
    Write-Host ('  File     : ' + $finalOut)
    Write-Host ('  Size     : ' + $mb + ' MB')
    Write-Host '  Duration : ~150 seconds'
    Write-Host '  Audio    : Microsoft David TTS, 44.1kHz AAC'
    Write-Host '  Video    : 1280x720 HD, 30fps'
    Write-Host '================================================'
} else {
    Write-Host 'ERROR: Final video file not created.'
    Write-Host ('Expected: ' + $finalOut)
}
