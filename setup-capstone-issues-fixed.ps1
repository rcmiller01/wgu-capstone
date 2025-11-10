# PowerShell script to create GitHub issues for WGU Capstone workflow
param(
    [Parameter(Mandatory=$true)]
    [string]$Repo,
    
    [Parameter(Mandatory=$false)]
    [string]$Owner = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectNumber = ""
)

# Set strict error handling
$ErrorActionPreference = "Stop"

# --- Configuration ---
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "Repository: $Repo"
Write-Host "Owner: $Owner" 
Write-Host "Project Number: $ProjectNumber"
Write-Host ""

# --- Preflight checks ---
Write-Host "Checking GitHub CLI installation..." -ForegroundColor Green
try {
    $ghVersion = gh --version
    Write-Host "GitHub CLI found: $($ghVersion.Split("`n")[0])"
} catch {
    Write-Error "GitHub CLI (gh) is not installed. Install from: https://cli.github.com/"
    exit 1
}

Write-Host "Checking GitHub authentication..." -ForegroundColor Green
try {
    gh auth status 2>&1 | Out-Null
    Write-Host "GitHub CLI is authenticated"
} catch {
    Write-Error "GitHub CLI is not authenticated. Run: gh auth login"
    exit 1
}

# Validate REPO parameter
if ($Repo -match "^<.*>$" -or $Repo -eq "") {
    Write-Error "Please provide a valid repository in the format 'owner/repo'"
    exit 1
}

# --- Labels ---
$Labels = @(
    @{name="phase:0-proposal"; color="8B949E"},
    @{name="phase:1-data"; color="8B949E"},
    @{name="phase:2-baseline"; color="8B949E"},
    @{name="phase:3-gather"; color="8B949E"},
    @{name="phase:4-methods"; color="8B949E"},
    @{name="phase:5-tooling"; color="8B949E"},
    @{name="phase:6-impl"; color="8B949E"},
    @{name="phase:7-analysis"; color="8B949E"},
    @{name="phase:8-results"; color="8B949E"},
    @{name="phase:9-writing"; color="8B949E"},
    @{name="phase:10-defense"; color="8B949E"},
    @{name="type:docs"; color="1F6FEB"},
    @{name="type:data"; color="1F6FEB"},
    @{name="type:code"; color="1F6FEB"},
    @{name="type:research"; color="1F6FEB"},
    @{name="type:review"; color="1F6FEB"},
    @{name="priority:P0"; color="d73a4a"},
    @{name="priority:P1"; color="fbca04"},
    @{name="priority:P2"; color="0e8a16"}
)

function Create-Label {
    param($Name, $Color)
    
    try {
        $existingLabels = gh label list -R $Repo --limit 200 | ConvertFrom-Json
        if ($existingLabels | Where-Object { $_.name -eq $Name }) {
            Write-Host "Label exists: $Name" -ForegroundColor Gray
        } else {
            gh label create $Name --color $Color -R $Repo | Out-Null
            Write-Host "Created label: $Name" -ForegroundColor Green
        }
    } catch {
        Write-Host "Label create failed (maybe exists): $Name" -ForegroundColor Yellow
    }
}

Write-Host "Creating labels..." -ForegroundColor Green
foreach ($label in $Labels) {
    Create-Label -Name $label.name -Color $label.color
}

# --- Issues helper ---
function Create-Issue {
    param($Title, $Body, $Labels)
    
    try {
        gh issue create -R $Repo --title $Title --body $Body --label $Labels | Out-Null
        Write-Host "Created: $Title" -ForegroundColor Green
    } catch {
        Write-Host "Failed to create issue: $Title" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

# --- Issues ---
Write-Host "Creating issues..." -ForegroundColor Green

Create-Issue "Phase 0 - Final proposal polish" "Ensure statistical terminology across name/topic/question/hypotheses; depersonalize voice; add context/contribution and in-text citations per rubric." "phase:0-proposal,type:docs,priority:P0"

Create-Issue "Phase 1 - Data source and variables table" "Link primary datasets; add variables table (name, role IV/DV, type); document volume/sparsity, reliability, usability, durability, and limitations vs. delimitations." "phase:1-data,type:research,type:docs,priority:P0"

Create-Issue "Phase 2 - Baseline and testing context" "Locate peer-reviewed/ops sources for manual ingestion baseline; add concise baseline statement + limitation; draft timing test plan and success thresholds." "phase:2-baseline,type:research,type:docs,priority:P0"

Create-Issue "Phase 3 - Data cleaning pipeline" "Implement cleaning in code (missingness policy, coercions, outlier strategy, quality metrics); track data lineage raw to clean to features." "phase:3-gather,type:code,type:data,priority:P1"

Create-Issue "Phase 4 - Study design and methods" "Normality checks; select and justify primary statistical methods (e.g., t-test/ANOVA/chi-square/logistic/regression). Define evaluation metrics and assumption tests." "phase:4-methods,type:docs,type:research,priority:P0"

Create-Issue "Phase 5 - Tooling justification" "Short compare/contrast R vs. Python vs. SAS with citations; lock final stack and environments." "phase:5-tooling,type:docs,priority:P2"

Create-Issue "Phase 6 - Reproducible repo skeleton" "Scaffold /data, /notebooks, /src, /docs; env files; Makefile/scripts; parameterization; random seeds; CI smoke checks for schema and NA thresholds." "phase:6-impl,type:code,priority:P0"

Create-Issue "Phase 7 - EDA and validation" "EDA tied to hypotheses; run primary analyses; sensitivity checks; document assumption violations and fixes." "phase:7-analysis,type:code,type:research,priority:P1"

Create-Issue "Phase 8 - Results and interpretation" "Report statistics with proper terms; state support for Ha; cite supporting literature; package reusable model artifact (saved model + usage notes)." "phase:8-results,type:docs,type:code,priority:P1"

Create-Issue "Phase 9 - Writing and APA polish" "Ensure in-text citations in all sections; finalize APA references; grammar/spell; signature page per course template." "phase:9-writing,type:docs,priority:P1"

Create-Issue "Phase 10 - Defense readiness" "Build slide deck and live demo path (sample run with timing vs. baseline); rehearse QA on assumptions, methods, privacy/ethics." "phase:10-defense,type:docs,priority:P1"

# Optional: add issues to a Projects v2 board
if ($ProjectNumber -and $ProjectNumber -ne "0" -and $Owner) {
    Write-Host "Adding issues to Projects v2 #$ProjectNumber for $Owner..." -ForegroundColor Green
    try {
        $recentIssues = gh issue list -R $Repo --search "created:@me sort:created-desc" --limit 20 --json number | ConvertFrom-Json
        foreach ($issue in $recentIssues) {
            try {
                gh project item-add --owner $Owner --project-number $ProjectNumber --url "https://github.com/$Repo/issues/$($issue.number)" | Out-Null
            } catch {
                # Ignore errors for project operations
            }
        }
    } catch {
        Write-Host "Could not add issues to project board" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Done! Review issues in $Repo and adjust priorities/assignees." -ForegroundColor Green