$raw = [Console]::In.ReadToEnd()
$json = $raw | ConvertFrom-Json
$file = $json.tool_input.file_path
if ($file -and ($file -match '\.py$') -and ($file -notmatch 'test_')) {
    $dir = Split-Path $file -Parent
    $base = [IO.Path]::GetFileNameWithoutExtension($file)
    $testPath = "$dir\tests\test_$base.py"
    if (-not (Test-Path $testPath)) {
        $ctx = "No test file found for $file. Create tests at $testPath before finishing this task."
        $out = '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"' + $ctx + '"}}'
        Write-Output $out
    }
}
