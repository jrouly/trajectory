// Run javascript after DOM is initialized
$(document).ready(function() {

  $('.collapse').on('show.bs.collapse', function () {
    $('.collapse.in').collapse('hide');
  });

  $('#search').hideseek({
    ignore: '.ignore'
  });

  $('#search').on('keypress', function() {
    $('.collapse.in').collapse('hide');
  });

  function expand_id() {
    var hash = window.location.hash, idx = hash.indexOf("#");
    if(idx == 0) {
      hash = hash.substring(idx+1);
      $(".collapse"+hash).collapse('show');
    }
  }
  expand_id();

});
