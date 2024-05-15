const form = document.querySelector("#signup-form");

//두 패스워드가 같을 때만 서버에게 보내기 위한 함수
const checkPW = () => {
  const formData = new FormData(form);
  const PW1 = formData.get("password");
  const PW2 = formData.get("password2");
  if (PW1 === PW2) {
    return true;
  } else return false;
};

const handleSubmit = async (event) => {
  event.preventDefault();
  //submit 버튼이 자동새로고침되지 않게 하기 위함.
  const formData = new FormData(form);
  const sha256pw = sha256(formData.get("password"));
  formData.set("password", sha256pw);
  //html에서 속성 name이 password인 것을 get해서 sha256으로 감싸서 암호화해주고
  //그 암호화된 값을 password에 다시 넣어준다.

  const div = document.querySelector("#info");

  if (checkPW()) {
    const res = await fetch("/signup", {
      method: "post",
      body: formData,
      //넣어준 값을 서버로 보내는 것
    });
    const data = await res.json();

    if (data === "200") {
      alert("회원가입이 완료되었습니다.");
      window.location.pathname = "/login.html";
    } //서버에서 처리완료가 된 return "200"을 받았을 때 회원가입 완료 알림 뜨게 하는 것
  } else {
    div.innerText = "비밀번호가 일치하지 않습니다.";
    div.style.color = "red";
  }
  //두 비밀번호가 같으면 서버로 보내고 다르면 div를 나타낸다.
};

form.addEventListener("submit", handleSubmit);
