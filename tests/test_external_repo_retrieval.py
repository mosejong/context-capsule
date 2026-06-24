from app.schemas.capsule_schema import RetrievalMode
from app.services.capsule_service import generate_capsule_result


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_english_product_repo(tmp_path):
    repo = tmp_path / "english_product"
    repo.mkdir()
    write(repo / "README.md", "# Shop App\nEnglish-only ecommerce demo.\n")
    write(
        repo / "backend" / "auth" / "login.py",
        "import jwt\n\ndef issue_token(user, mobile=False):\n    return jwt.encode({'sub': user.id}, 'secret')\n",
    )
    write(
        repo / "frontend" / "src" / "cart.js",
        "export function addToCart(product) {\n  return { type: 'cart/add', payload: product };\n}\n",
    )
    write(
        repo / "docker-compose.yml",
        "services:\n  api:\n    build: ./backend\n    environment:\n      - APP_ENV=production\n",
    )
    write(repo / "docs" / "deployment.md", "Deployment guide for docker compose and nginx.\n")
    return repo


def relevant_paths(repo, task):
    result = generate_capsule_result(
        repo_path=repo,
        task_request=task,
        retriever_mode=RetrievalMode.KEYWORD,
    )
    return [chunk.path for chunk in result.capsule.relevant_chunks], result


def test_korean_login_request_finds_english_login_file(tmp_path):
    repo = write_english_product_repo(tmp_path)

    paths, result = relevant_paths(repo, "로그인이 모바일에서만 안돼")

    assert "backend/auth/login.py" in paths[:3]
    assert result.capsule.relevant_chunks


def test_korean_cart_request_finds_english_cart_file(tmp_path):
    repo = write_english_product_repo(tmp_path)

    paths, _ = relevant_paths(repo, "장바구니 기능 추가")

    assert "frontend/src/cart.js" in paths[:3]


def test_korean_deploy_request_prefers_deploy_config(tmp_path):
    repo = write_english_product_repo(tmp_path)

    paths, _ = relevant_paths(repo, "배포 설정 고쳐")

    assert "docker-compose.yml" in paths[:3] or "docs/deployment.md" in paths[:3]
