$(document).ready(function(){

  function disable_buttons(){
    $('.card').css('pointer-events', 'none');
    $('#end_turn').css('pointer-events', 'none');
    $('.switch').css('pointer-events', 'none');
  }

  function generate_clue() {
     $('#turn_text').html("Generating a clue");

     $.ajax({
        type:'POST',
        url: "{{ url_for('clue')}}",
        contentType: "application/json; charset=utf-8",
        dataType: "html",
        data: JSON.stringify(board),
        success: function(clue_details){
            clue_details = JSON.parse(clue_details);
            clue = clue_details.clue;
            targets = clue_details.targets;
            board[0]["invalid_guesses"].push(clue);
            $("#clue_text").html(`Clue: ${clue} (${targets.length})`)
            remaining_guesses = targets.length + 1;
            update_card_borders(cheat);
            make_guess();
        }
    });
  };

  function make_guess() {
    $('#turn_text').html("Make your guesses");
    disable_buttons();
    $('.card').css('pointer-events', 'auto');
    $('#end_turn').css('pointer-events', 'auto');
    $('.switch').css('pointer-events', 'auto');
  }

  function update_card_borders(check) {
    for (i = 0; i < targets.length; i++) {
      id = targets[i];
      if (check == true || board[id].active == true) {
          $("#"+id).css({
          "color": white,
          "text-shadow": text_shadow});
      }
      else {
        $("#"+id).css({
        "color": "black",
        "text-shadow": ""});
      }
    }
  }

  //Update card
  function update_card(id) {

    //Set the card to active
    board[id].active = true;

    //Change its colour
    $("#"+id).css({
    "color": white,
    "text-shadow": text_shadow,
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
    if (end == true) {
        return;
    }
    console.log(blue_remaining, red_remaining, assassin_remaining);
    if (blue_remaining == 0) {
      //Update title
      $('#turn_text').html("You win!");
      end = true;
    }
    //The computer never chooses the assassin so no assassin guarantees a loss
    else if (red_remaining == 0 || assassin_remaining == 0) {
      //Update title
      $('#turn_text').html("You lose...");
      end = true;
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
         sequence = JSON.parse(sequence).sequence;

         //Apply the sequence
         sequence_length = sequence.length;
         for (i = 0; i < sequence_length; i++) {
            update_card(sequence[i]);
            if (check_end() == true) {
                break;
            }
         }
         //If the game hasn't ended, generate another clue
         if (check_end() == false) {
            generate_clue();
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
  var targets = [];
  var clue_details = '';
  var clue = '';
  var end = false;
  var sequence = [];
  var sequence_length = 0;
  var id = 0;
  var white = "#F5F5F5";
  var text_shadow = "0 0 1px black, 0 0 1px black, 0 0 1px black, 0 0 1px black";
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
  generate_clue();

  /*
  Click events
  */

  // Card behaviour
  $('.card').click(function() {
     // Get the id of the card
     id = $(this).attr('id');

     if (board[id].active == false) {
        // Remove a guess
        remaining_guesses -= 1;

        // Update the clicked card
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

  //Instruction button behaviour
  $('#instructions').click(function() {
    theDialog.dialog("open");
  });

  //End turn button behaviour
  $('#end_turn').click(function() {
    computer_turn();
  });

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