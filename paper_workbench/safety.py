"""Repository data-safety checks for release readiness."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

from . import __version__


FORBIDDEN_SUFFIXES = {".pdf", ".pyc", ".sqlite", ".db"}
FORBIDDEN_PARTS = {".paperwb", ".pytest_cache", ".idea", ".ipynb_checkpoints", "__pycache__"}
FORBIDDEN_NAMES = {".DS_Store"}
TEXT_SUFFIXES = {".bib", ".csv", ".json", ".md", ".py", ".ris", ".toml", ".txt", ".yaml", ".yml"}
ABSOLUTE_PATH_PATTERNS = [
    re.compile(r"/Users/[^\s`|,\"]+"),
    re.compile(r"/private/[^\s`|,\"]+"),
    re.compile(r"file://[^\s`|,\"]+"),
    re.compile(r"[A-Za-z]:\\[^\s`|,\"]+\\[^\s`|,\"]+"),
]
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
PUBLISHER_BYPASS_TERMS = ("sci-" + "hub",)
PUBLIC_DEMO_PREFIX = "public/demos/"
PUBLIC_DEMO_PDF_PATTERN = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9_.-]*\.pdf\b", re.IGNORECASE)
DEFAULT_DATA_SAFETY_TITLE = f"Data Safety Audit v{__version__}"
ABSOLUTE_PATH_WARNING_ALLOWLIST = {
    "reports/hostile_review_v0_4.md",
    "reports/hostile_review_v0_5.md",
    "reports/release_readiness_v0_3.md",
    "reports/release_readiness_v0_6.md",
    "tests/test_integrity_backup_migration_v0_9.py",
    "tests/test_release_hygiene.py",
    "tests/test_v2_release_candidate.py",
}


@dataclass(slots=True)
class SafetyFinding:
    severity: str
    code: str
    path: str
    message: str


@dataclass(slots=True)
class SafetyAuditResult:
    root: str
    files_checked: int
    findings: list[SafetyFinding]

    @property
    def errors(self) -> list[SafetyFinding]:
        return [finding for finding in self.findings if finding.severity == "error"]

    @property
    def warnings(self) -> list[SafetyFinding]:
        return [finding for finding in self.findings if finding.severity == "warning"]


def tracked_files(root: str | Path = ".") -> list[Path]:
    root_path = Path(root)
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root_path, check=True, text=True, capture_output=True)
    return [root_path / line for line in result.stdout.splitlines() if line.strip()]


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_text_if_possible(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def _skip_absolute_path_content_scan(relative_path: str) -> bool:
    return relative_path in ABSOLUTE_PATH_WARNING_ALLOWLIST or bool(re.fullmatch(r"reports/data_safety(?:_audit)?_v[0-9A-Za-z_]+\.md", relative_path))


def _public_demo_metadata_findings(relative_path: str, content: str) -> list[SafetyFinding]:
    if not relative_path.startswith(PUBLIC_DEMO_PREFIX):
        return []

    findings: list[SafetyFinding] = []
    path = Path(relative_path)
    lower_content = content.lower()
    name = path.name.lower()

    if name == "registry.csv":
        data_rows = [line for line in content.splitlines()[1:] if line.strip()]
        unsafe_rows = [line for line in data_rows if "synthetic" not in line.lower() and "placeholder" not in line.lower()]
        if unsafe_rows:
            findings.append(
                SafetyFinding(
                    "error",
                    "public_demo_real_metadata",
                    relative_path,
                    "Public demo registry rows must be synthetic placeholders, not real paper metadata.",
                )
            )

    if path.suffix.lower() == ".bib" and "@" in content and "synthetic" not in lower_content and "placeholder" not in lower_content:
        findings.append(
            SafetyFinding(
                "error",
                "public_demo_real_metadata",
                relative_path,
                "Public demo BibTeX entries must be synthetic placeholders, not copied real bibliography metadata.",
            )
        )

    if path.suffix.lower() == ".md":
        unsafe_pdf_names = [
            match.group(0)
            for match in PUBLIC_DEMO_PDF_PATTERN.finditer(content)
            if "synthetic" not in match.group(0).lower() and "placeholder" not in match.group(0).lower()
        ]
        if unsafe_pdf_names:
            findings.append(
                SafetyFinding(
                    "error",
                    "public_demo_private_filename",
                    relative_path,
                    "Public demo Markdown mentions PDF filenames that do not look synthetic; keep real dogfood filenames untracked.",
                )
            )

    return findings


def audit_data_safety(root: str | Path = ".", *, max_file_bytes: int = 1_000_000) -> SafetyAuditResult:
    root_path = Path(root)
    findings: list[SafetyFinding] = []
    files = tracked_files(root_path)
    for path in files:
        rel = _relative(path, root_path)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or path.name in FORBIDDEN_NAMES or any(part in FORBIDDEN_PARTS for part in path.parts):
            findings.append(SafetyFinding("error", "forbidden_tracked_artifact", rel, "Forbidden generated, cache, database, or PDF artifact is tracked."))
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            findings.append(SafetyFinding("error", "tracked_file_missing", rel, "Tracked file is missing from the working tree."))
            continue
        if size > max_file_bytes:
            findings.append(SafetyFinding("warning", "large_tracked_file", rel, f"Tracked file is larger than {max_file_bytes} bytes."))
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        content = _read_text_if_possible(path)
        if not content:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                findings.append(SafetyFinding("error", "possible_secret", rel, f"Text matches secret pattern `{pattern.pattern}`."))
                break
        if not _skip_absolute_path_content_scan(rel):
            absolute_scan_content = "\n".join(line for line in content.splitlines() if "re.compile" not in line)
            for pattern in ABSOLUTE_PATH_PATTERNS:
                if pattern.search(absolute_scan_content):
                    findings.append(SafetyFinding("warning", "absolute_local_path", rel, f"Text contains local absolute-path pattern `{pattern.pattern}`."))
                    break
        if any(term in content.lower() for term in PUBLISHER_BYPASS_TERMS):
            findings.append(SafetyFinding("warning", "publisher_bypass_reference", rel, "Text mentions a publisher-bypass source."))
        if path.suffix.lower() == ".txt" and any(part in {"text", "papers"} for part in path.parts) and size > 20_000:
            findings.append(SafetyFinding("warning", "large_text_sidecar", rel, "Tracked text sidecar is large; confirm it is synthetic or user-owned text."))
        findings.extend(_public_demo_metadata_findings(rel, content))
    return SafetyAuditResult(root=str(root_path), files_checked=len(files), findings=findings)


def safety_audit_markdown(
    result: SafetyAuditResult,
    *,
    max_findings_per_code: int = 20,
    title: str = DEFAULT_DATA_SAFETY_TITLE,
) -> str:
    counts = Counter(finding.code for finding in result.findings)
    lines = [
        f"# {title}",
        "",
        "This audit checks tracked and unignored repository files. It does not inspect ignored user caches, local PDFs, or ignored private files.",
        "",
        f"Root: {result.root}",
        f"Repository files checked: {result.files_checked}",
        f"Errors: {len(result.errors)}",
        f"Warnings: {len(result.warnings)}",
        "",
        "## Summary By Code",
        "",
        "| Code | Count |",
        "| --- | ---: |",
    ]
    if counts:
        for code, count in sorted(counts.items()):
            lines.append(f"| {code} | {count} |")
    else:
        lines.append("| none | 0 |")
    lines.extend(["", "## Findings", ""])
    if not result.findings:
        lines.append("No tracked data-safety findings detected.")
    else:
        emitted_by_code: Counter[str] = Counter()
        for finding in result.findings:
            emitted_by_code[finding.code] += 1
            if emitted_by_code[finding.code] > max_findings_per_code:
                continue
            lines.append(f"- **{finding.severity} {finding.code}** `{finding.path}`: {finding.message}")
        for code, count in sorted(counts.items()):
            if count > max_findings_per_code:
                lines.append(f"- **warning truncated_{code}**: {count - max_findings_per_code} additional `{code}` findings omitted from this report.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Errors should block release until fixed.",
            "- Warnings identify release-hygiene risks, including historical reports that may contain machine-local paths.",
            "- The audit does not prove that user-supplied text is copyright-safe; examples must remain synthetic and reviewable.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
