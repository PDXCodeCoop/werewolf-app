
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/trivia" + window.location.pathname);
var baseURL = window.location.protocol + '//' + window.location.host


function getPlayerVotes() {
    $('.vote').click(function() {
       var command = {
           room: $('#room_label').val(),
           game: $('#game_id').val(),
           target: $(this).attr('value'),
           voter: $("#player_id").attr("value"),
           turn: $("#turnVal").val(),
           category: $(this).attr('category'),
       }
       //alert(JSON.stringify(command))
       chatsock.send(JSON.stringify(command));
       return false;
       });
}

function getUserData() {
    player_id = $("#player_id").attr("value")
    game_id = $('#game_id').val()
    $.ajax({url: baseURL + "/api-view/players/"+player_id+"/?format=json", async:false, success: function(result){
        $(".usernameValue").text(result.name);
        $("#role").val(result.role.label);
        $(".roleValue").text(result.role.name);
        $("#roleDescription").text(result.role.description);
        $("#abilityDescription").text(result.role.description_abilities);
    }});
}

function setPlayers(turn) {
    var active_players = []
    var teammates = []
    var active_players_element = $('<ul id="players_vote"></ul>')
    var active_players_werewolf_element = $('<ul id="werewolf_vote"></ul>')
    var active_players_seer_element = $('<ul id="seer_vote"></ul>')
    for (i = 0, len = turn.players.length; i < len; i++) {
        turn.players[i].vote = 0
        turn.players[i].ww_vote = 0
        turn.players[i].seer_vote = 0
        active_players.push(turn.players[i].pk)
        for (j = 0, vote_len = turn.votes.length; j < vote_len; j++){
            if (turn.players[i].pk == turn.votes[j].target){
                if (turn.votes[j].category == "player"){
                    turn.players[i].vote += 1
                }
                if ($("#role").val() == "werewolf"){
                    if (turn.votes[j].category == "werewolf"){
                        turn.players[i].ww_vote += 1
                    }
                }
                if ($("#role").val() == "seer"){
                    if (turn.votes[j].category == "seer"){
                        turn.players[i].seer_vote += 1
                    }
                }
            }
        }
    }
    if ($.inArray(parseInt($("#player_id").attr("value")), active_players) >= 0) {
        $(".statusValue").text("ALIVE")
        $("#status").val("ALIVE")
        for (i = 0, len = turn.players.length; i < len; i++) {
            active_players_element.append("<a class='vote btn btn-option' href='#' category='player' value="+ turn.players[i].pk +">"
                + turn.players[i].name
                + "<span class='vote_num'> ("+ turn.players[i].vote +" votes)</span></a>");
        }
        //If Werewolf
        if ($("#role").val() == "werewolf"){
            for (i = 0, len = turn.players.length; i < len; i++) {
                if (turn.players[i].role.label == "werewolf"){
                    teammates.push(turn.players[i])
                }
                active_players_werewolf_element.append("<a class='vote btn btn-option' category='werewolf' href='#' value="+ turn.players[i].pk +">"
                    + turn.players[i].name
                    + "<span class='vote_num'> ("+ turn.players[i].ww_vote +" votes)</span></a>");
            }
        }
        //If Seer
        if ($("#role").val() == "seer"){
            for (i = 0, len = turn.players.length; i < len; i++) {
                active_players_seer_element.append("<a class='vote btn btn-option' category='seer' href='#' value="+ turn.players[i].pk +">"
                    + turn.players[i].name
                    + "<span class='vote_num'> ("+ turn.players[i].seer_vote +" votes)</span></a>");
            }
        }
    }else{
        $("#status").val("DEAD")
        $(".statusValue").text("DEAD")
        active_players_element.append("<p>Dead people can't vote! Just sit back, keep quiet, and enjoy watching the game.</p>")
    }

    $(".current_players").html(active_players_element);
    teammates_display = "Your teammates are: "
    for (i = 0, len = teammates.length; i < len; i++) {
        teammates_display += teammates[i].name + ", "
    }
    if ($("#role").val() == "werewolf"){
        $("#action_result").text(teammates_display)
        $("#action_description").text("Choose a Victim:")
        $(".current_players_action").html(active_players_werewolf_element);
    }
    if ($("#role").val() == "seer"){
        $("#action_description").text("Choose someone to their identity:")
        $(".current_players_action").html(active_players_seer_element);
    }
    getPlayerVotes()

}

function getLatestTurn() {
    var game_id = $('#game_id').val()
    $.ajax({url: baseURL + "/api-view/games/"+game_id+"/?format=json", async: true, success: function(result){
        var latest_turn = result.turns[result.turns.length - 1]
        setPlayers(latest_turn)
        $(".turnValue").text(latest_turn.counter)
        $("#turnVal").attr("value", latest_turn.pk)
        if (result.turns.length >= 2){
            var previous_turn = result.turns[result.turns.length - 2]
            if ($("#role").val() == "seer"){
                for (j = 0, vote_len = previous_turn.votes.length; j < vote_len; j++){
                    if (previous_turn.votes[j].category == "seer"){
                        console.log(previous_turn)
                        for (i = 0, player_len = previous_turn.players.length; i < player_len; i++){
                            if (previous_turn.players[i].pk == previous_turn.votes[j].target){
                                seer_result_name = previous_turn.players[i].name
                                seer_result_role = previous_turn.players[i].role.name
                                $("#action_result").text(seer_result_name + " is a " + seer_result_role)
                            }
                        }

                    }
                }
            }
        }

    }});

}

$(function() {
    getUserData()
    getLatestTurn()
    getPlayerVotes()
    console.log(window.location.protocol + '//' + window.location.host)
    // When we're using HTTPS, use WSS too.
    chatsock.onmessage = function(command) {
        var data = JSON.parse(command.data);
        console.log(data)
        if (data.finished != null){
            window.location = baseURL + "/werewolf/result/" + $('#room_label').val();
        }

        getUserData()
        getLatestTurn()
    };
});
