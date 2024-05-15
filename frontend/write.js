const form = document.getElementById("write-form");

const handleSubmitForm = async (event) => {
  event.preventDefault();
  //submit 버튼이 자동새로고침되지 않게 하기 위함.
  const body = new FormData(form);
  body.append("insertAT", new Date().getTime());
  //현재 시간을 같이 폼 데이터에 보내주기 위함.
  //body.append = body에 어떤 정보를 추가한다는 문법
  try {
    const res = await fetch("/items", {
      method: "POST",
      body,
    });
    const data = await res.json();
    if (data === "200") window.location.pathname = "/";
    console.log("complete");
  } catch (e) {
    console.error("이미지 업로드에 실패했습니다.");
  }
};
form.addEventListener("submit", handleSubmitForm);
//try-catch 문법= try안에 있는 로직을 시도하다가 그 안에서 에러가 발생하면 catch안에 있는 로직이 실행되는 문법
//fetch를 items라는 주소로 보낼 것이다. fetch를 하게 되면 res(response, 응답)가 오게한다.
//main.py에 post로 items주었기에 method는 post
//body는 form data형식인데 위에서 작성한 함수 body값을 넣어준다. :body지워도 인식함(body: body; 일 경우)
//python 서버에서 완료되면 200을 보내주기로 작성해놓음(return '200')
//그 data값을 json으로 바꾸어주고 만약 그 data값이 서버에서 보내주기로 한 200이면
//window.location이라는 객체를 참고해서 pathname을 루트(/)로 바꾼다.
//그렇지 않으면 콘솔에서 '이미지 업로드에 실패했습니다.'라는 에러는 표시한다.
//글쓰기를 완료하고 나서 서버에서 완성이 되었으면 다시 메인페이지(루트페이지)로 이동시키고 아니면 오류를 보내는 로직
//id=write-form에서 submit이벤트가 발생하면 handleSubmitForm함수를 실행시킨다.
