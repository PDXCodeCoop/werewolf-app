var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/trivia" + window.location.pathname);
var baseURL = window.location.protocol + '//' + window.location.host
var room = $('#room_label').val()
var game = $('#game_id').val()
var player_id = $('#player_id').val()

$(function() {
    $('#assign_roles_button').click(function() {
        var command = {
            room: room,
            game: game,
            assign: true,
        }
        //alert(JSON.stringify(command))
        chatsock.send(JSON.stringify(command));
        return false;
    });

    chatsock.onmessage = function(command) {
        var data = JSON.parse(command.data);
        if (data.assign == true){
            window.location = baseURL + "/werewolf/remote/" + room;
        }
        if (data.players != null){
            var player_list = $("<ul id = 'player_list'></ul>")
            for (i = 0, len = data.players.length; i < len; i++) {
                player_list.append("<li>"+data.players[i].name+"</li>");
            }
            $("#player_list").replaceWith(player_list)
        }
        console.log(data)
    }
});
