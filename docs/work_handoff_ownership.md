# Work Handoff Ownership Check

Work Handoff Ownership Check helps a user ask:

```text
이 작업이 내 파트인가?
다른 사람 파트를 건드릴 가능성이 있나?
PR이나 회의에서 먼저 확인해야 하나?
```

It is designed for junior developers and team-project situations where task scope is easy to blur.

## How To Use

In the FastAPI dashboard:

```text
AI에게 작업 맡기기
-> 내 담당 영역
-> 하고 싶은 작업 입력칸
-> 작업 정리본 만들기
-> 내 파트 확인
```

Example:

```text
내 담당 영역:
README, UI, frontend

하고 싶은 작업:
로그인 오류 고쳐줘
```

The result will show one of:

```text
내 파트 가능성 높음
다른 파트 가능성
확인 필요
```

## CLI

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "리드미 손보자" --my-scope "README, docs" --json
```

The JSON output includes:

```json
{
  "ownership_check": {
    "status": "likely_my_part",
    "notes": [],
    "questions": []
  }
}
```

## What It Does Not Do

Ownership Check does not:

- evaluate teammates
- score contribution
- assign work automatically
- create branches automatically
- approve code changes

It only asks safer follow-up questions before a user sends a handoff packet to AI, a teammate, or GitHub Issue.

## Matching Rule

The checker compares:

- the user's declared scope, such as `README`, `frontend`, `backend/auth`
- the task request
- retrieved candidate file paths

Paths are split into useful tokens. For example:

```text
README.md -> readme
app/auth.py -> app, auth
backend/auth/login.py -> backend, auth, login
```

If the overlap is clear, the result is `likely_my_part`.
If the request points to a different area, the result can be `possibly_other_part`.
If the evidence is weak, the result stays `needs_confirmation`.
