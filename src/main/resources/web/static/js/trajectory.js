// Run javascript after DOM is initialized
$(document).ready(function() {

  $('.collapse').on('show.bs.collapse', function () {
    $('.collapse.in').collapse('hide');
  });

  $('#search-universities').hideseek({ });

  $('#search-topics').hideseek({ });

  function expand_course() {
    var hash = window.location.hash, idx = hash.indexOf("#");
    if(idx == 0) {
      hash = hash.substring(idx+1);
      $(".collapse"+hash).collapse('show');
    }
  }
  expand_course();

});
