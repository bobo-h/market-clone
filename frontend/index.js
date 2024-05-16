//장소와 시간을 함께 넣을 건데 타임정보는 타임스탬프(숫자)로 해서 보냈고 밑에서 MetaDiv에서 받아왔다.
//그 숫자를 다시 현재시간과 비교해서 현재시간과 얼마나 차이나는 지를 표시해야 한다.(함수로 따로 만드는 것이 용이)
//그리고 그 차이를 시간에 관련된 값으로 바꾸어줘야한다.
const calcTime = (timestamp) => {
  //한국시간 = 세계시간 + 9 이기에 보낼때부터 한국시간으로 보내거나 받을 때 세계시간 기준으로 계산해 받아야한다.
  const curTime = new Date().getTime() - 9 * 60 * 60 * 1000;
  const time = new Date(curTime - timestamp);
  const hour = time.getHours();
  const minute = time.getMinutes();
  const second = time.getSeconds();

  //시간이 0이면 띄우지 않게 하기 위함(백틱으로 문자열로 바꾸어 리턴한다.)
  if (hour > 0) return `${hour}시간 전`;
  else if (minute > 0) return `${minute}분 전`;
  else if (second > 0) return `${second}초 전`;
  else return "방금 전";
};

//가져온 데이터를 기준으로 화면 구현 업데이트 하기
const renderData = (data) => {
  const main = document.querySelector("main");
  //받아온 데이터가 오브젝트가 안에 들어있는 array 형태로 왔다.
  //forEach구문은 array에만 쓸 수 있다. 각각의 array 내부에 있는, 배열 내부에 있는 각각의 항목을 돌면서 그것에 대한 값을 실행하게 된다.
  //최신글을 위에 작성하기 위해 array를 뒤집어 주는 문법인 reverse를 사용해야한다.
  data.reverse().forEach(async (obj) => {
    const div = document.createElement("div");
    div.className = "item-list";

    const imgDiv = document.createElement("div");
    imgDiv.className = "item-list__img";

    const img = document.createElement("img");
    const res = await fetch(`/images/${obj.id}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    img.src = url;
    //블롭으로 저장된 이미지를 받아와서 자바스크립트에서 변환해주는 과정이 필요하다.(서버요청필요)

    const InfoDiv = document.createElement("div");
    InfoDiv.className = "item-list__info";

    const InfoTitleDiv = document.createElement("div");
    InfoTitleDiv.className = "item-list__info-title";
    InfoTitleDiv.innerText = obj.title;

    const InfoMetaDiv = document.createElement("div");
    InfoMetaDiv.className = "item-list__info-meta";
    InfoMetaDiv.innerText = obj.place + " " + calcTime(obj.insertAT);
    //타임스탬프가 calcTime함수에 전달된다.

    const InfoPriceDiv = document.createElement("div");
    InfoPriceDiv.className = "item-list__info-price";
    InfoPriceDiv.innerText = obj.price;

    imgDiv.appendChild(img);
    InfoDiv.appendChild(InfoTitleDiv);
    InfoDiv.appendChild(InfoMetaDiv);
    InfoDiv.appendChild(InfoPriceDiv);
    div.appendChild(imgDiv);
    div.appendChild(InfoDiv);
    main.appendChild(div);
  });
};

//서버로부터 데이터 받아오기
const fetchList = async () => {
  const accessToken = window.localStorage.getItem("token");
  const res = await fetch("/items", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (res.status === 401) {
    alert("로그인이 필요합니다.");
    window.location.pathname = "/login.html";
    return;
  }
  const data = await res.json();
  renderData(data);
};
//write.js에선 items를 method: "POST"로 어떤 값을 생성하게 했는데(서버에서도 post로 받음)
//이번에는 어떤 값을 조회하는(CRUD중에 R,read를 담당하는) get요청을 보내(아무것도 없는 기본값이 get임)
//서버에서 @app.get('/items')로 받아 items의 list를 보내주는 형식으로 만들어야함
//서버에 보낼 때 인증된 토큰을 headers에서 가져와서(getItem) 같이 보내줘야한다.

//만든 함수 호출
fetchList();
