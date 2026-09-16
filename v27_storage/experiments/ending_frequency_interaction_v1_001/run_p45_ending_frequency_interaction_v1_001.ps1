$ErrorActionPreference = 'Stop'
$out = Split-Path -Parent $MyInvocation.MyCommand.Path
Add-Type -Path (Join-Path $out 'p45_ending_frequency_interaction_v1_001.cs')
[EndingFrequencyV1]::Run('E:\P45 프로젝트')
