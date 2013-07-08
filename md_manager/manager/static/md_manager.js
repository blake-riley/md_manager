$(document).ready(function() {
var isVisible = false;
var clickedAway = false;
var was_popover_button_click = false;

$('.make_popover').each(function() {
    $(this).popover({
        html: true,
        trigger: 'manual'
    }).click(function(e) {
      var curr_button = this;

      $(curr_button).popover('show');
      $(".make_popover").each(function(i, el) {
        if(el != curr_button) {
          $(el).popover('hide');
        }
      });
      //isVisible = true;
      was_popover_button_click = true;
      //e.preventDefault();
    });
});


  $(document).click(function(e) {
    //if(isVisible & clickedAway)
    //{
      if(!was_popover_button_click) $('.make_popover').popover('hide');
      //isVisible = clickedAway = false;
    //}
    //else
    //{
    //  clickedAway = true;
    //}

    if(was_popover_button_click) was_popover_button_click = false;
  });
});