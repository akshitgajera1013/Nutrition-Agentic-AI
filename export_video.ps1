# export_video.ps1 — Export NutriGuide PPTX to 150-second MP4

$pptxPath  = (Resolve-Path 'NutriGuide_Agentic_AI.pptx').Path
$videoPath = (Split-Path $pptxPath) + '\NutriGuide_Agentic_AI_Video.mp4'

Write-Host '================================================'
Write-Host '  NutriGuide Agentic AI - Video Export'
Write-Host '  PPTX to MP4 - 150 seconds total'
Write-Host '================================================'
Write-Host ''
Write-Host ('Source : ' + $pptxPath)
Write-Host ('Output : ' + $videoPath)
Write-Host ''

Write-Host '[1/4] Starting PowerPoint COM...'
$pptApp = New-Object -ComObject PowerPoint.Application
$pptApp.Visible = [Microsoft.Office.Core.MsoTriState]::msoFalse

Write-Host '[2/4] Opening presentation...'
$pres = $pptApp.Presentations.Open($pptxPath, $false, $false, $false)
$slideCount = $pres.Slides.Count
Write-Host ('      Slides: ' + $slideCount)

$secPerSlide = [math]::Round(150 / $slideCount, 2)
Write-Host ('[3/4] Setting ' + $secPerSlide + ' sec per slide...')

foreach ($slide in $pres.Slides) {
    $slide.SlideShowTransition.AdvanceOnTime = $true
    $slide.SlideShowTransition.AdvanceTime   = $secPerSlide
    $slide.SlideShowTransition.EntryEffect   = 35
    $slide.SlideShowTransition.Speed         = 2
}

Write-Host '[4/4] Exporting to MP4 at 1280x720 HD...'
$pres.CreateVideo($videoPath, $true, $secPerSlide, 720, 30, 85)

Write-Host '      Rendering - please wait...'
$maxWait = 270
$waited  = 0

while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 5
    $waited += 5
    if (Test-Path $videoPath) {
        $sz = (Get-Item $videoPath).Length
        Write-Host ('      ' + $waited + 's - size: ' + [math]::Round($sz/1MB,1) + ' MB')
        if ($sz -gt 1MB) {
            Start-Sleep -Seconds 8
            $sz2 = (Get-Item $videoPath).Length
            if ($sz2 -ge $sz) {
                Write-Host '      Export complete - file stable!'
                break
            }
        }
    } else {
        Write-Host ('      ' + $waited + 's - rendering...')
    }
}

$pres.Save()
$pres.Close()
$pptApp.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($pres)   | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($pptApp) | Out-Null
[gc]::Collect()

if (Test-Path $videoPath) {
    $mb = [math]::Round((Get-Item $videoPath).Length / 1MB, 2)
    Write-Host ''
    Write-Host '================================================'
    Write-Host '  VIDEO EXPORT COMPLETE!'
    Write-Host ('  File     : ' + $videoPath)
    Write-Host ('  Size     : ' + $mb + ' MB')
    Write-Host '  Duration : ~150 seconds'
    Write-Host '  Quality  : 1280x720 HD, 30fps'
    Write-Host '================================================'
} else {
    Write-Host ''
    Write-Host 'WARNING: File not found. PowerPoint may need more time.'
    Write-Host ('Check: ' + $videoPath)
}
