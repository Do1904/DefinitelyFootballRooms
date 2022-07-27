//関数内からwsを参照出来る様にするために一旦nullで定義(変数のスコープについて調べてみても良いかも)
let ws = null;
//参照するdomを定数に格納
const inputNickname = document.getElementById("name")
const nameSettingButton = document.getElementById("setName")
const sendButton = document.getElementById("send")
const msgText = document.getElementById("message")
const nameArea = document.getElementById("nameArea")
// const pub = document.getElementById("pub")

const nameSetting = () => {
    const nickname = inputNickname.value
    //名前は一度しか使用しないのでdomを削除するためのリストを作成
    const removableDoms = [inputNickname,nameSettingButton]
    //disabledを削除したいdomのリストを作成
    const abeledDoms = [sendButton,msgText]
    nameArea.innerText = nickname
    removeDom(removableDoms)
    abledChatSpace(abeledDoms)
}   

//使わないdomを削除するための関数
//doms=array 
const removeDom = (doms) => {
    doms.forEach((dom) => dom.remove())
}
//domのdisable属性を削除するための関数
const abledChatSpace = (doms) => {
    doms.forEach((dom) => dom.disabled = false)
}

//data = string
const updateLog = ( data ) => {
    //stringで帰ってくるのでjson形式にする。
    data = JSON.parse(data)
    const p = document.createElement('p');
    p.innerText = `${data.nickname} : ${data.message}`
    chatSpace.appendChild(p)	
}

const connectWsServer = () => {
    //webSocketのクラスをインスタンス化する。(最初に作っておいた変数wsに代入する)
    ws = new WebSocket(`ws://localhost:8000/community/${fd}/chat?nickname=${nameArea.innerText}`)
    //wsの接続が確立された時の処理
    ws.onopen = function() {
        //wsからmessageが来た時の処理。
        ws.onmessage = function( msg ) {
            updateLog( msg.data ) ;
        }
    }    
}

//入力されたテキストをjson形式の文字列に変換
const getMessage = () => {
    const msg = {
        message: msgText.value
    }
    return JSON.stringify(msg)
}
//wsのエンドポイントに上の関数をの戻り値を送信する
const sendMessage = () => {
    //メッセージが空の場合は送信できない様にする。
     if (!msgText.value) {
        alert("文字を入力してから送信してください")
        return
    }
    const msg = getMessage()
    ws.send(msg)
}

sendButton.addEventListener("click", sendMessage)
nameSettingButton.addEventListener("click", nameSetting)
nameSettingButton.addEventListener("click",connectWsServer)