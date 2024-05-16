const form = document.querySelector("#login-form");

const handleSubmit = async (event) => {
  event.preventDefault();
  // submit 버튼이 자동새로고침되지 않게 하기 위함.
  const formData = new FormData(form);
  const sha256pw = sha256(formData.get("password"));
  formData.set("password", sha256pw);
  // html에서 속성 name이 password인 것을 get해서 sha256으로 감싸서 암호화해주고
  // 그 암호화된 값을 password에 다시 넣어준다.

  const res = await fetch("/login", {
    method: "post",
    body: formData,
    // 넣어준 값을 서버로 보내는 것
  });
  const data = await res.json();
  const accessToken = data.access_token;
  window.localStorage.setItem("token", accessToken);
  // 엑세스토큰을 로컬 스토리지에 저장하는 것. window의 localStoage에 새로 추가한다{setItem(key,value)}
  // key는 정해주면 된다. token이라는 키로 정함. f12 - Application - local storage에 들어가면 토큰 확인가능
  alert("로그인이 완료되었습니다.");

  window.location.pathname = "/";
};

form.addEventListener("submit", handleSubmit);
