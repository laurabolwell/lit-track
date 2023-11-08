$(document).ready(function () {
  $('.sidenav').sidenav({ edge: "right" });
  $('select').formSelect();
  $('.collapsible').collapsible();
  $('.datepicker').datepicker({
    format: "dd mmmm, yyyy",
    yearRange: 0,
    autoClose: true,
  });