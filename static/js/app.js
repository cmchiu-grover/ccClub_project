function agreeCheck(event) {
  const checkbox = document.getElementById("agree");

  if (!checkbox.checked) {
    alert("請先勾選同意條款。");
    event.preventDefault();
  }
}
