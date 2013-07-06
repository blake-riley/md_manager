$(document).ready(function() {
var isVisible = false;
var clickedAway = false;

$('.make_popover').each(function() {
    $(this).popover({
        html: true,
        trigger: 'manual'
    }).click(function(e) {
        $(this).popover('show');
        isVisible = true;
        //e.preventDefault();
    });
});

$(document).click(function(e) {
  if(isVisible & clickedAway)
  {
     $('.make_popover').each(function() {
          $(this).popover('hide');
     });
    isVisible = clickedAway = false;
  }
  else
  {
    clickedAway = true;
  }
});
});