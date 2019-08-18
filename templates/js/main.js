
// Equivalent to time.sleep(). Only works on async functions.
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

$(document).ready(function(){

  //Update the page based on the current board state
  function update() {
    $.ajax({
       type:'POST',
       url: "{{ url_for('update')}}",
       contentType: "application/json; charset=utf-8",
       dataType: "html",
       data: JSON.stringify(board),
       success: function(response){
         console.log(response);
         $("body").html(response);
       }
    });
  }

  var board = {{board|tojson|safe}};

  console.log(board[0]);

  //Load instructions
  var opt = {
     autoOpen: false,
     resizable: false,
     title: "Instructions",
     text: $('#dialog').load("instructions"),
     height: 500,
     width: 500
  };
  var theDialog = $("#dialog").dialog(opt);

  //Set difficulty
  var difficulty = board[0].difficulty;
  $("#"+difficulty).prop("checked", true);

  //Disable useless clue buttons
  for (i = 1; i < 4 - board[0].blue_remaining; i++) {
     var button_number = 4-i;
     $('#clue_button'+button_number).css('pointer-events', 'none');
  }

  //Check for gameover
  if (board[0].red_remaining == 0 || board[0].assassin_remaining == 0) {
    board[0].state = "lose";
  }
  else if (board[0].blue_remaining == 0) {
    board[0].state = "win";
  }

  //Act upon the state
  async function state_handler() {
      if (board[0].state == "lose"){
        $('.card').css('pointer-events', 'none');
        $('.clue_button').css('pointer-events', 'none');
        $('#end_turn').css('pointer-events', 'none');
        //Make all cards active
        do_update = false;
        for (j = 1; j < 26; j++) {
            if (board[j].active == false){
                board[j].active = true;
                do_update = true;
            }
        }
        if (do_update == true) {
            update();
        }
      }
      else if (board[0].state == "win"){
        $('.card').css('pointer-events', 'none');
        $('.clue_button').css('pointer-events', 'none');
        $('#end_turn').css('pointer-events', 'none');
        //Make all cards active
        do_update = false;
        for (j = 1; j < 26; j++) {
            if (board[j].active == false){
                board[j].active = true;
                do_update = true;
            }
        }
        if (do_update == true) {
            update();
        }
      }
      else if (board[0].state == "computer_turn") {
        $('.card').css('pointer-events', 'none');
        $('.clue_button').css('pointer-events', 'none');
        $('#end_turn').css('pointer-events', 'none');
        //If you haven't got a sequence yet, generate one
        if (board[0].sequence.length == 0) {
            $.ajax({
               type:'POST',
               url: "{{ url_for('computer_turn')}}",
               contentType: "application/json; charset=utf-8",
               dataType: "html",
               data: JSON.stringify(board),
               success: function(response){
                 console.log(response);
                 $("body").html(response);
               }
            });
        } else {
            //Apply the choices from the sequence
            name = board[0].sequence.shift();
            for (j = 1; j < 26; j++) {
                if (board[j].name == name) {
                    board[j].active = true;
                    if (board[j].type == "blue") {
                        board[0].blue_remaining -= 1;
                    }
                    else if (board[j].type == "red") {
                        board[0].red_remaining -= 1;
                    }
                    else if (board[j].type == "neutral") {
                        board[0].neutral_remaining -= 1;
                    }
                    //No assassin if statement here because computer never chooses the assassin
                }
            }
            if (board[0].sequence.length == 0) {
                board[0].state = "choose_clue";
            }
            await sleep(1000);
            update();
        }
      } else if (board[0].state == "make_guess") {
        $('.clue_button').css('pointer-events', 'none');
      } else if (board[0].state == "choose_clue") {
        $('.card').css('pointer-events', 'none');
        $('#end_turn').css('pointer-events', 'none');
      }

  }
  state_handler();

  //Card behaviour
  $('div[class=card]').click(function() {
     // If the card is not active
     if (board[$(this).data('id')].active == false) {
        // Set the card to active
        board[$(this).data('id')].active = true;
        // Decrement the appropriate counts
        board[0].remaining_guesses -= 1;
        if (board[0].remaining_guesses == 0) {
            board[0].state = "computer_turn"
        }
        if (board[$(this).data('id')].type == "blue") {
            board[0].blue_remaining -= 1;
        } else if (board[$(this).data('id')].type == "red") {
            board[0].red_remaining -= 1;
            board[0].state = "computer_turn";
        } else if (board[$(this).data('id')].type == "neutral"){
            board[0].neutral_remaining -= 1;
            board[0].state = "computer_turn";
        } else if (board[$(this).data('id')].type == "assassin"){
            board[0].assassin_remaining -= 1;
        }
     }
     update();
  });

  //Reset button behaviour
  $('div[id=reset]').click(function() {
     $.ajax({
        type:'POST',
        url: "/",
        dataType: "html",
        success: function(response){
          console.log(response);
          $("body").html(response);
        }
    });
  });

  //Clue button behaviour
  $('.clue_button').click(function() {
     //Stop other requests
     $('.clue_button').css('pointer-events', 'none');
     //Loading placeholder
     $('div[id=clue]').html("thinking...");
     board[0].target = $(this).data('target');
     board[0].remaining_guesses = board[0].target + 1;
     $.ajax({
        type:'POST',
        url: "{{ url_for('clue')}}",
        contentType: "application/json; charset=utf-8",
        dataType: "html",
        data: JSON.stringify(board),
        success: function(response){
          console.log(response);
          $("body").html(response);
        }
    });
  });

  //Instruction button behaviour
  $('div[id=instructions]').click(function() {
    theDialog.dialog("open");
    return false;
  });

  //End turn button behaviour
  $('div[id=end_turn]').click(function() {
    board[0].state = "computer_turn";
    update();
  })

  //Radio button behaviour
  $("input[name='difficulty']").click(function(){
    board[0].difficulty = $("input[name='difficulty']:checked").val();
  });

  $("input[type='radio']").checkboxradio();
});