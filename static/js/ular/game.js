//static/js/ular/game.js

function opentab(tab, close = "no")
{
    const divcreateroom = document.getElementById('divcreateroom');
    const divjoinroom = document.getElementById('divjoinroom');
    const divboard = document.getElementById('divboard');
    const btnCreate = document.getElementById('btnCreate');
    const btnJoin = document.getElementById('btnJoin');

    if (tab == "create")
    {
        divcreateroom.style.display = "block";
        if (close == "yes")
        {
            divjoinroom.style.display = "none";
            divboard.style.display = "none";
            // Style active tab
            btnCreate.style.backgroundColor = "#4CAF50";
            btnCreate.style.color = "white";
            btnCreate.style.borderBottom = "2px solid #4CAF50";
            // Reset inactive tab
            btnJoin.style.backgroundColor = "#f0f0f0";
            btnJoin.style.color = "black";
            btnJoin.style.borderBottom = "2px solid transparent";
        }
    }
    else if (tab == "join")
    {
        divjoinroom.style.display = "block";
        if (close == "yes")
        {
            divcreateroom.style.display = "none";
            divboard.style.display = "none";
            // Style active tab
            btnJoin.style.backgroundColor = "#2196F3";
            btnJoin.style.color = "white";
            btnJoin.style.borderBottom = "2px solid #2196F3";
            // Reset inactive tab
            btnCreate.style.backgroundColor = "#f0f0f0";
            btnCreate.style.color = "black";
            btnCreate.style.borderBottom = "2px solid transparent";
        }
    }
    else if (tab == "board")
    {
        divboard.style.display = "block";
        if (close == "yes")
        {
            divcreateroom.style.display = "none";
            divjoinroom.style.display = "none";
        }
    }
}

function showdiv(id)
{
    const div = document.getElementById(id);
    div.style.display = "block";
}
function hidediv(id)
{
    const div = document.getElementById(id);
    div.style.display = "none";
}

//starting screen
showdiv("divcreatejoin");
showdiv("divcreateroom");
hidediv("divjoinroom");
hidediv("divrefreshgame");
hidediv("divboard");
hidediv("divquestion");

const board = document.getElementById('board');
const diceR = document.getElementById('diceR');
const rollDice = document.getElementById('rollDice');

const maxBox = 28;
const rows = 4;
const cols = 7;

// ------------------ BUILD BOARD ------------------
function setCell(i) {
  const cell = document.createElement('div');
  cell.classList.add('cell');
  cell.textContent = i;

  // sample snakes/ladders
  if ([15, 23, 17, 9].includes(i)) cell.classList.add('snake');
  if ([16, 18, 8, 3].includes(i)) cell.classList.add('ladder');

  board.appendChild(cell);
}

// draw in zigzag order
for (let r = rows - 1; r >= 0; r--) {
  const leftToRight = r % 2 === 0;
  for (let c = 0; c < cols; c++) {
    const num = r * cols + (leftToRight ? c + 1 : cols - c);
    setCell(num);
  }
}

// ------------------ GAME STATE ------------------
let playerPositions = {};  // playerId -> position
let playerColors = {};     // playerId -> color
let playerElements = {};   // playerId -> DOM element

const cells = [
    {
      "x": -10,
      "y": 110
    },
    {
      "x": 0,
      "y": 90
    },
    {
      "x": 30,
      "y": 90
    },
    {
      "x": 60,
      "y": 90
    },
    {
      "x": 90,
      "y": 90
    },
    {
      "x": 120,
      "y": 90
    },
    {
      "x": 150,
      "y": 90
    },
    {
      "x": 180,
      "y": 90
    },
    {
      "x": 180,
      "y": 60
    },
    {
      "x": 150,
      "y": 60
    },
    {
      "x": 120,
      "y": 60
    },
    {
      "x": 90,
      "y": 60
    },
    {
      "x": 60,
      "y": 60
    },
    {
      "x": 30,
      "y": 60
    },
    {
      "x": 0,
      "y": 60
    },
    {
      "x": 0,
      "y": 30
    },
    {
      "x": 30,
      "y": 30
    },
    {
      "x": 60,
      "y": 30
    },
    {
      "x": 90,
      "y": 30
    },
    {
      "x": 120,
      "y": 30
    },
    {
      "x": 150,
      "y": 30
    },
    {
      "x": 180,
      "y": 30
    },
    {
      "x": 180,
      "y": 0
    },
    {
      "x": 150,
      "y": 0
    },
    {
      "x": 120,
      "y": 0
    },
    {
      "x": 90,
      "y": 0
    },
    {
      "x": 60,
      "y": 0
    },
    {
      "x": 30,
      "y": 0
    },
    {
      "x": 0,
      "y": 0
    }
  ];

function addPlayer(playerId, color = 'red') {
  // prevent duplicates
  if (playerElements[playerId]) return;

  const player = document.createElement('div');
  player.classList.add('player');
  player.dataset.playerId = playerId;
  player.style.backgroundColor = color;
  board.appendChild(player);

  playerPositions[playerId] = 1;
  playerColors[playerId] = color;
  playerElements[playerId] = player;

  movePlayer(playerId, 0);
}

function movePlayer(playerId, newPos) {
  const player = playerElements[playerId];
  const pos = cells[newPos];
  console.log(player);
  console.log(pos);
  if (!player || !pos) return;

  player.style.transform = `translate(${pos.x + 5}px, ${pos.y + 5}px)`;
  playerPositions[playerId] = newPos;
}

function getPlayerColor(id) {
  return playerColors[id] || 'gray';
}

// optional snakes/ladders map
const jumps = {
  3: 11, 8: 16,
  15: 5, 23: 14
};

// ------------------ API SIMULATION EXAMPLE ------------------
// Example for `/state` call:
// Call updateState({ players: [{id:'P1',pos:5,color:'red'}, ...] })
function updateState(data) {
  data.players.forEach(p => {
    addPlayer(p.id, p.color);
    movePlayer(p.id, p.pos);
  });
}

// Helper function to get player color
function getPlayerColor(playerId) {
    return playerColors[playerId] || 'gray';
}

function setcode(code) {
    const result = document.getElementById("codeR");
    result.innerHTML = "code: " +code;
}
function setplayer(player) {
    const result = document.getElementById("playerR");
    if (player == "" || player == undefined)
    {
        result.innerHTML = "";
    }
    else
    {
        result.innerHTML = "player: " +player;
    }
}
function setplayers(players) {
    const result = document.getElementById("playersR");
    if (players == "" || players == undefined)
    {
        result.innerHTML = "";
    }
    else
    {
        var html = "";
        html += "<div>";

        players.forEach(item => {
            html += "<div style='display:flex;justify-content:center;align-items:center;'>";
            html += `${item.player} - ${item.pos} `
            html += `<div style='border-radius:24px;background-color:${item.color};width:28px;height:28px;'> </div> `
            html += "</div>"
            setpos("")
            setcolor("")

        });
        html += "</div>"
        result.innerHTML = html;
    }
}
function setcolor(color) {
    const result = document.getElementById("colorR");
    if (color == "" || color == undefined)
    {
        result.innerHTML = "";
    }
    else
    {
        result.innerHTML = "color: " +color;
    }
}
function setpos(pos) {
    const result = document.getElementById("posR");
    if (pos == "" || pos == undefined)
    {
        result.innerHTML = "";
    }
    else
    {
        result.innerHTML = "pos: " +pos;
    }
}
function setstate(state) {
    const result = document.getElementById("stateR");
    if (state == "waiting")
    {
        result.innerHTML = "state: " +state + "<button class='btn btn-success' onclick='startgame();'>Start</button>";
    }
    else
    {
        result.innerHTML = "state: " +state;
    }
    
}
function setdice(dice) {
    const result = document.getElementById("diceR");
    const result2 = document.getElementById("diceR2");
    if (dice == "" || dice == undefined)
    {
        result.innerHTML = "";
    }
    else
    {
        result.innerHTML = "Dice: " + dice;
        result2.innerHTML = "🎲";
        result2.style.transition = "transform 0.5s ease";
        result2.style.transform = "rotate(360deg)";
        setTimeout(() => {
            result2.style.transform = "rotate(0deg)";
        }, 500);
    }
    
}

function createroom() {
    const player = document.getElementById("playercreateroom").value;
    const color = document.getElementById("colorcreateroom").value;
    // const maxbox = document.getElementById("maxboxcreateroom").value;
    const maxbox = 28;
    const topic = document.getElementById("topiccreateroom").value;
    const outputall = document.getElementById("outputall");
    const code2 = document.getElementById("statecode");
    const player2 = document.getElementById("playercode");
    outputall.innerHTML = "Creating room...";
    fetch(`/api/ular/createroom?player=${encodeURIComponent(player)}&color=${encodeURIComponent(color)}&maxbox=${encodeURIComponent(maxbox)}&topic=${encodeURIComponent(topic)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => response.json()).then(data => {
        console.log(data);
        if (data.status == "ok")
        {
            var message = data.message;
            outputall.innerHTML = message;
            // setcode(data.code);
            // setplayer(data.player);
            // setcolor(data.color);
            // setpos(data.pos);
            // setstate(data.state);
            // opentab("board", "yes");
            hidediv("divcreatejoin");
            hidediv("divcreateroom");
            hidediv("divjoinroom");
            hidediv("divquestion");
            code2.value = data.code;
            player2.value = data.player;
            showdiv("divrefreshgame");
            showdiv("divboard");

            refreshgame();
            // Start auto-refresh when successfully creating a room
            startAutoRefresh();
            // outputcreateroom.innerHTML = JSON.stringify(data, null, 2);
        }
        else
        {
            if (data.status == "error")
            {
                var message = data.message;
                outputall.innerHTML = message;
            } 
            else
            {
                var message = "Something error when connecting server. Please check your internet connection.";
                outputall.innerHTML = message;
            }
        }
    }).catch(error => {
        outputall.innerHTML = "Error: " + error;
    });
}

function joinroom() {
    const code = document.getElementById("codejoinroom").value;
    const player = document.getElementById("playerjoinroom").value;
    const color = document.getElementById("colorjoinroom").value;
    const outputall = document.getElementById("outputall");
    const code2 = document.getElementById("statecode");
    const player2 = document.getElementById("playercode");
    outputall.innerHTML = "Joining room...";
    fetch(`/api/ular/joinroom?code=${encodeURIComponent(code)}&player=${encodeURIComponent(player)}&color=${encodeURIComponent(color)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => response.json()).then(data => {
        console.log(data);
        if (data.status == "ok")
        {
            var message = data.message;
            outputall.innerHTML = message;
            // setcode(data.code);
            // setplayer(data.player);
            // setplayers(data.players);
            // setcolor(data.color);
            // setpos(data.pos);
            // setstate(data.state);
            // opentab("board", "yes");
            hidediv("divcreatejoin");
            hidediv("divcreateroom");
            hidediv("divjoinroom");
            hidediv("divquestion");
            code2.value = data.code;
            player2.value = data.player;
            showdiv("divrefreshgame");
            showdiv("divboard");
            
            refreshgame();
            // Start auto-refresh when successfully joining a room
            startAutoRefresh();
            // outputcreateroom.innerHTML = JSON.stringify(data, null, 2);
        }
        else
        {
            if (data.status == "error")
            {
                var message = data.message;
                outputall.innerHTML = message;
            } 
            else
            {
                var message = "Something error when connecting server. Please check your internet connection.";
                outputall.innerHTML = message;
            }
        }
    }).catch(error => {
        outputall.innerHTML = "Error: " + error;
    });
}


function refreshgame()
{
    const code = document.getElementById("statecode").value;
    const outputall = document.getElementById("outputall");
    // outputall.innerHTML = "Refreshing...";
    fetch(`/api/ular/state?code=${encodeURIComponent(code)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => response.json()).then(data => {
        console.log(data);
        if (data.status == "ok")
        {
            var message = data.message;
            outputall.innerHTML = message;
            setcode(data.code);
            setplayer(data.player);
            setplayers(data.players);
            setcolor("");
            setpos("");
            setstate(data.state);
            opentab("board", "yes");

            //move player UI
            data.players.forEach(playerData => {
                const playerId = playerData.player;     // Unique player identifier
                // const oldPos = playerPositions[playerId] || 0;   // Previous position from stored state
                const newPos = playerData.pos;      // New position
                playerColors[playerId] = playerData.color; // Store player color
                addPlayer(playerId, playerData.color);
                movePlayer(playerId, newPos);
            });

            hidediv("divquestion");
            // showdiv("boardinfo");
            showdiv("boardinfo2");

            // console.log(data.question.length);
            if (data.question.length != 0)
            {
                // outputall.innerHTML = message;
                showdiv("divquestion");
                // hidediv("divboard");
                // hidediv("boardinfo");
                hidediv("boardinfo2");
                document.getElementById("questionplayertext").innerHTML = "Answerer: " + data.turn;
                document.getElementById("questiontext").innerHTML = data.question[0].question;
                document.getElementById("a1text").innerHTML = data.question[0].a1;
                document.getElementById("a2text").innerHTML = data.question[0].a2;
                document.getElementById("a3text").innerHTML = data.question[0].a3;
                document.getElementById("a4text").innerHTML = data.question[0].a4;
            }
            // outputcreateroom.innerHTML = JSON.stringify(data, null, 2);
        }
        else
        {
            if (data.status == "error")
            {
                var message = data.message;
                outputall.innerHTML = message;
            } 
            else
            {
                var message = "Something error when connecting server. Please check your internet connection.";
                outputall.innerHTML = message;
            }
        }
    }).catch(error => {
        outputall.innerHTML = "Error: " + error;
    });
}

function startgame() {
    const code = document.getElementById("statecode").value;
    const outputall = document.getElementById("outputall");
    outputall.innerHTML = "Starting game...";
    fetch(`/api/ular/startgame?code=${encodeURIComponent(code)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => response.json()).then(data => {
        console.log(data);
        if (data.status == "ok")
        {
            var message = data.message;
            outputall.innerHTML = message;
            setplayer("");
            setplayers(data.players);
            setcolor("");
            setpos("");
            setstate(data.state);
        }
        else
        {
            if (data.status == "error")
            {
                var message = data.message;
                outputall.innerHTML = message;
            } 
            else
            {
                var message = "Something error when connecting server. Please check your internet connection.";
                outputall.innerHTML = message;
            }
        }
    }).catch(error => {
        outputall.innerHTML = "Error: " + error;
    });
}

function rolldice() {
    const code = document.getElementById("statecode").value;
    const player = document.getElementById("playercode").value;
    const outputall = document.getElementById("outputall");
    // outputall.innerHTML = "Rolling dice...";
    fetch(`/api/ular/rolldice?code=${encodeURIComponent(code)}&player=${encodeURIComponent(player)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => response.json()).then(data => {
        console.log(data);
        if (data.status == "ok")
        {
            var message = data.message;
            outputall.innerHTML = message;
            setcode(data.code);
            setplayer(data.player);
            setplayers(data.players);
            setcolor("");
            setpos("");
            setstate(data.state);
            setdice(data.dice);
            
            //move player UI
            data.players.forEach(playerData => {
                const playerId = playerData.player;     // Unique player identifier
                // const oldPos = playerPositions[playerId] || 0;   // Previous position from stored state
                const newPos = playerData.pos;      // New position
                playerColors[playerId] = playerData.color; // Store player color
                movePlayer(playerId, newPos);
            });

            hidediv("divquestion");
            // showdiv("boardinfo");
            showdiv("boardinfo2");
            

            // opentab("board", "yes");
            if (data.question.length != 0)
            {
                showdiv("divquestion");
                // hidediv("divboard");
                // hidediv("boardinfo");
                hidediv("boardinfo2");
                document.getElementById("questionplayertext").innerHTML = "Answerer: " + data.turn;
                document.getElementById("questiontext").innerHTML = data.question[0].question;
                document.getElementById("a1text").innerHTML = data.question[0].a1;
                document.getElementById("a2text").innerHTML = data.question[0].a2;
                document.getElementById("a3text").innerHTML = data.question[0].a3;
                document.getElementById("a4text").innerHTML = data.question[0].a4;
            }
        }
        else
        {
            if (data.status == "error")
            {
                var message = data.message;
                outputall.innerHTML = message;
            } 
            else
            {
                var message = "Something error when connecting server. Please check your internet connection.";
                outputall.innerHTML = message;
            }
        }
    }).catch(error => {
        outputall.innerHTML = "Error: " + error;
    });
}

function jawab(answer) {
    // console.log("aaaaa");
    console.log(answer);
    // showdiv("divboard");
    const code = document.getElementById("statecode").value;
    const player = document.getElementById("playercode").value;
    const outputall = document.getElementById("outputall");
    // outputall.innerHTML = "Submitting answer...";
    fetch(`/api/ular/submitanswer?code=${encodeURIComponent(code)}&player=${encodeURIComponent(player)}&answer=${encodeURIComponent(answer)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => response.json()).then(data => {
        console.log(data);
        if (data.status == "ok")
        {
            var message = data.message;
            // outputall.innerHTML = message;
            //javascript popup message message
            alert(message);

            setplayers(data.players);
            // setpos(data.pos);
            setstate(data.state);
            
            //move player UI
            data.players.forEach(playerData => {
                const playerId = playerData.player;     // Unique player identifier
                // const oldPos = playerPositions[playerId] || 0;   // Previous position from stored state
                const newPos = playerData.pos;      // New position
                playerColors[playerId] = playerData.color; // Store player color
                movePlayer(playerId, newPos);
            });
            
            hidediv("divquestion");
            // showdiv("boardinfo");
            showdiv("boardinfo2");
        }
        else
        {
            if (data.status == "error")
            {
                var message = data.message;
                outputall.innerHTML = message;
            } 
            else
            {
                var message = "Something error when connecting server. Please check your internet connection.";
                outputall.innerHTML = message;
            }
        }
    }).catch(error => {
        outputall.innerHTML = "Error: " + error;
    });
}

function submitanswer() {
    const code = document.getElementById("codesubmitanswer").value;
    const player = document.getElementById("playersubmitanswer").value;
    const answer = document.getElementById("answersubmitanswer").value;
    const output = document.getElementById("outputsubmitanswer");
    output.innerHTML = "Submitting answer...";
    fetch(`/api/ular/submitanswer?code=${encodeURIComponent(code)}&player=${encodeURIComponent(player)}&answer=${encodeURIComponent(answer)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => response.json()).then(data => {
        output.innerHTML = JSON.stringify(data, null, 2);
    }).catch(error => {
        output.innerHTML = "Error: " + error;
    });
}

function reset() {
    const outputcreateroom = document.getElementById("outputcreateroom");
    outputcreateroom.innerHTML = "";
    const outputjoinroom = document.getElementById("outputjoinroom");
    outputjoinroom.innerHTML = "";
    const outputstate = document.getElementById("outputstate");
    outputstate.innerHTML = "";
    const outputstartgame = document.getElementById("outputstartgame");
    outputstartgame.innerHTML = "";
    const outputrolldice = document.getElementById("outputrolldice");
    outputrolldice.innerHTML = "";
}

let refreshInterval = null;

function startAutoRefresh() {
    if (refreshInterval === null) {
        refreshInterval = setInterval(refreshgame, 1000);
    }
}

function stopAutoRefresh() {
    if (refreshInterval !== null) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}