var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/trivia" + window.location.pathname);
var baseURL = window.location.protocol + '//' + window.location.host
var room = $('#room_label').val()
var game = $('#game_id').val()
var player_id = $('#player_id').val()

$(function() {
    $('#new_game').click(function() {
        var command = {
            room: $(this).val(),
            game: $('#game_id').val(),
            new_game: true,
        }
        console.log(JSON.stringify(command))
        chatsock.send(JSON.stringify(command));
        return false;
    });

    chatsock.onmessage = function(command) {
        var data = JSON.parse(command.data);
        if (data.new_game != null){
            window.location = baseURL + "/werewolf/newgame/" + room;
            //$("#assign_roles_form").submit()
        }
        console.log(data)
    }
});
