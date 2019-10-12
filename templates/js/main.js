//Equivalent to time.sleep(). Only works on async functions.
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

$(document).ready(function(){

  //Disable the clue, card and end turn buttons
  function disable_buttons(){
    $('.card').css('pointer-events', 'none');
    $('#end_turn').css('pointer-events', 'none');
    $('.clue_button').css('pointer-events', 'none');
    $('.switch').css('pointer-events', 'none');
  }

  //Make guesses
  function make_guess() {
    //Update title
    $('#turn_text').html("Make your guesses");

    //Activate relevant buttons
    disable_buttons();
    $('.card').css('pointer-events', 'auto');
    $('#end_turn').css('pointer-events', 'auto');
    $('.switch').css('pointer-events', 'auto');
  }

  //Choose clue
  function choose_clue() {
    //Update title
    $('#turn_text').html("Choose a clue size");

    //Activate relevant buttons
    disable_buttons();
    $('.clue_button').css('pointer-events', 'auto');
  }

  //Update card borders
  function update_card_borders(check) {
    if (check == true) {
      var outline_style = "dashed";
    }
    else {
      var outline_style = "none";
    }
    for (i = 0; i < target_blue.length; i++) {
      var id = target_blue[i];
      $("#"+id).css({
      "outline-style": outline_style});
    }
  }

  //Update card
  function update_card(id) {

    //Set the card to active
    board[id].active = true;

    //Change its colour
    $("#"+id).css({
    "color": "#F5F5F5",
    "background-color": board[id].colour});

    //Decrement the appropriate count
    if (board[id].type == "blue") {
        blue_remaining -= 1;
        $('#blue').html(blue_remaining);
    } else if (board[id].type == "red") {
        red_remaining -= 1;
        $('#red').html(red_remaining);
    } else if (board[id].type == "neutral"){
        neutral_remaining -= 1;
    } else if (board[id].type == "assassin"){
        assassin_remaining -= 1;
    }
  }

  //Check if the game has ended
  function check_end() {
    var end = false;
    //The computer never chooses the assassin so no assassin guarantees a loss
    if (red_remaining == 0 || assassin_remaining == 0) {
      //Update title
      $('#turn_text').html("Unlucky... You lose");
      var end = true;
    }
    else if (blue_remaining == 0) {
      //Update title
      $('#turn_text').html("Congratulations! You win");
      var end = true;
    }
    if (end == true) {
      //Disable all buttons
      disable_buttons();

      //Reveal the cards
      for (i = 1; i < 26; i++) {
        if (board[i].active == false) {
            update_card(i);
        }
      }
    }
    return end;
  }

  //Computer turn
  function computer_turn() {
    //Remove old cheat borders
    update_card_borders(false);

    //Update title
    $('#turn_text').html("Opponent's turn");

    //Update clue text
    $("#clue_text").html(`Clue: `)

    //Disable buttons
    disable_buttons();

    //Get a computer sequence
    $.ajax({
       type:'POST',
       url: "{{ url_for('computer_turn')}}",
       contentType: "application/json; charset=utf-8",
       dataType: "html",
       data: JSON.stringify(board),
       success: async function(sequence){
         var sequence = JSON.parse(sequence).sequence;

         //Apply the sequence
         var sequence_length = sequence.length;
         for (i = 0; i < sequence_length; i++) {
            await sleep(1000);
            update_card(sequence[i]);
            if (check_end() == true) {
                break;
            }
         }
         //If the game hasn't ended, go back to offering clues
         if (check_end() == false) {
            choose_clue();
         }
       }
    });
  }

  /*
  Setup
  */

  var board = {{board|tojson|safe}};
  var remaining_guesses = 0;
  var blue_remaining = 9;
  var red_remaining = 8;
  var neutral_remaining = 7;
  var assassin_remaining = 1;
  var cheat = false;
  window.target_blue = [];

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

  //Radio button setup
  $("input[type='radio']").checkboxradio();
  $("#easy").prop("checked", true);

  //Set the initial state
  choose_clue();

  /*
  Click events
  */

  //Card behaviour
  $('.card').click(function() {
     //Get the id of the card
     var id = $(this).attr('id');

     if (board[id].active == false) {
        // Remove a guess
        remaining_guesses -= 1;

        //Update the clicked card
        update_card(id);
        check_end();

        // It's the computers turn if we have no guesses or if we choose a bad card
        if (remaining_guesses == 0 || board[id].type != "blue") {
            computer_turn();
        }
     }
  });

  //Reset button behaviour
  $('#reset').click(function() {
     $.ajax({
        type:'POST',
        url: "/",
        dataType: "html",
        success: function(response){
          $("body").html(response);
        }
    });
  });

  //Clue button behaviour
  $('.clue_button').click(function() {

     //Stop other requests
     $('.clue_button').css('pointer-events', 'none');

     //Loading placeholder
     $('div[id=clue_text]').html("Thinking...");

     //Update the board
     board[0].target = $(this).data('target');
     remaining_guesses = board[0].target + 1;

     $.ajax({
        type:'POST',
        url: "{{ url_for('clue')}}",
        contentType: "application/json; charset=utf-8",
        dataType: "html",
        data: JSON.stringify(board),
        success: function(clue_details){
            var clue_details = JSON.parse(clue_details);
            var clue = clue_details.clue;
            window.target_blue = clue_details.target_blue;

            //Add the clue to the list of invalid guesses
            board[0]["invalid_guesses"].push(clue);

            //Update clue and target
            $("#clue_text").html(`Clue: ${clue} (${board[0].target})`)

            //Update borders of relevant cards
            update_card_borders(cheat);

            //Go to make_guess function
            make_guess();
        }
    });
  });

  //Instruction button behaviour
  $('#instructions').click(function() {
    theDialog.dialog("open");
  });

  //End turn button behaviour
  $('#end_turn').click(function() {
    computer_turn();
  })

  //Radio button behaviour
  $("input[name='difficulty']").click(function(){
    board[0].difficulty = $("input[name='difficulty']:checked").val();
  });

  //Cheat button behaviour
  $("#cheat").click(function(){
    cheat = this.checked;
    update_card_borders(cheat);
  });
});