from flask import Flask, render_template_string, request
import os
import json

app = Flask(__name__)

DATA_ROOT = "vote_system"
CLASS_DIR = os.path.join(DATA_ROOT, "classes")
CANDIDATE_FILE = os.path.join(DATA_ROOT, "candidates.json")

def load_candidates():
    with open(CANDIDATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

VOTE_FORM_TEMPLATE = """
<!doctype html>
<title>{{ class_name }} 투표</title>
<h2>{{ class_name }} - 전교회장 & 전교부회장 투표</h2>
<form method="post">
  <p><strong>전교회장 후보:</strong><br>
    {% for name in president %}
      <input type="radio" name="president" value="{{ name }}"> {{ name }}<br>
    {% endfor %}
  </p>
  <p><strong>전교부회장 후보:</strong><br>
    {% for name in vice_president %}
      <input type="radio" name="vice_president" value="{{ name }}"> {{ name }}<br>
    {% endfor %}
  </p>
  <input type="submit" value="투표 제출">
</form>
"""

SUCCESS_PAGE = """
<!doctype html>
<title>투표 완료</title>
<h3>투표가 성공적으로 완료되었습니다.</h3>
"""

@app.route("/vote/<class_name>", methods=["GET", "POST"])
def vote(class_name):
    class_file = os.path.join(CLASS_DIR, f"{class_name}.json")
    if not os.path.exists(class_file):
        return f"<h3>존재하지 않는 반입니다: {class_name}</h3>", 404

    candidates = load_candidates()
    president = candidates["president_candidates"]
    vice_president = candidates["vice_president_candidates"]

    if request.method == "POST":
        pres = request.form.get("president")
        vp = request.form.get("vice_president")
        if not pres or not vp:
            return "<h3>회장과 부회장 모두 선택해야 합니다.</h3>", 400

        with open(class_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["president"][pres] += 1
        data["vice_president"][vp] += 1
        data["voted"] = True

        with open(class_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return SUCCESS_PAGE

    return render_template_string(VOTE_FORM_TEMPLATE, class_name=class_name, president=president, vice_president=vice_president)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)