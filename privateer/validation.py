from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    code: str
    message: str
    critical: bool = True


@dataclass
class ValidationReport:
    total_ships: int = 0
    resolved_design_refs: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(issue.critical for issue in self.issues)

    def add(self, code: str, message: str, critical: bool = True) -> None:
        self.issues.append(ValidationIssue(code, message, critical))

    def __str__(self) -> str:
        lines = ["Fleet Validation", f"Total ships: {self.total_ships}",
                 f"Resolved design refs: {self.resolved_design_refs} / {self.total_ships}",
                 f"Critical errors: {sum(i.critical for i in self.issues)}"]
        lines.extend(f"- {item.code}: {item.message}" for item in self.issues)
        return "\n".join(lines)


class SaveValidationError(ValueError):
    def __init__(self, report: ValidationReport):
        super().__init__(str(report))
        self.report = report
