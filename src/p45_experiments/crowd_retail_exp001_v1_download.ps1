param([int]$StartRound=262,[int]$EndRound=1237)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$cache=Join-Path $root 'v27_storage\experiments\crowd_retail_exp001_v1\official_raw'
New-Item -ItemType Directory -Force -Path $cache | Out-Null
$rounds=$StartRound..$EndRound | Where-Object { -not (Test-Path (Join-Path $cache ("round-{0:D4}.json" -f $_))) }
$rounds | ForEach-Object -Parallel {
  $n=$_; $target=Join-Path $using:cache ("round-{0:D4}.json" -f $n)
  $headers=@{'Referer'='https://www.dhlottery.co.kr/wnprchsplcsrch/home';'User-Agent'='Mozilla/5.0'}
  $url="https://www.dhlottery.co.kr/wnprchsplcsrch/selectLtWnShp.do?srchWnShpRnk=1&srchLtEpsd=$n&srchShpLctn="
  $last=$null
  for($try=1;$try -le 3;$try++) {
    try {
      $content=(Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing -TimeoutSec 15).Content
      $obj=$content|ConvertFrom-Json
      if($null -eq $obj.data.list){throw 'NO_LIST'}
      [System.IO.File]::WriteAllText($target,$content,[System.Text.UTF8Encoding]::new($false)); return
    } catch {$last=$_; Start-Sleep -Milliseconds (500*$try)}
  }
  throw "FETCH_FAILED:${n}:$last"
} -ThrottleLimit 4
"DOWNLOADED=$((Get-ChildItem -LiteralPath $cache -Filter 'round-*.json').Count)"
