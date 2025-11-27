# hi

<p id="hellojs3" />
<script>
document.write("hello");
</script>
</p>

Today is a beautiful day

<h2>display things</h2>

<button type="button"
onclick="document.getElementById('hellojs').innerHTML = 'Hello JavaScript!'">
Click me to display Date and Time.</button>

<p id="hellojs">hiiiiiii</p>
<!-- change the content of the element with id="hellojs" -->

<h2>Welcome to My Page</h2>
<button onclick='document.getElementById("hellojs1").innerHTML = "Hello JavaScript!";'>Click me</button>
<script>
    function myFunction() {
        document.getElementById("hellojs1").innerHTML = "Hello JavaScript!";
    }
</script>

<p id="hellojs1">This is a paragraph that will be changed.</p>

<h2>button for date</h2>

<button type="button"
onclick="document.getElementById('datebutton').innerHTML = Date()">
Click me to display Date and Time.</button>

<p id="datebutton"></p>
<!-- change the content of the element with id="datebutton" -->

<h2>button for date</h2>

<p id="datebutton1"></p>

<script id="hellojs1">
document.getElementById('datebutton1').innerHTML = Date()
</script>
<!-- Do not change the content of the element with id="hellojs1" -->

# Interactive Demo (Works with Markdown Preview Enhanced)

<button onclick="myFunction()">Click me</button>

<script>
    function showMessage() {
        document.getElementById("outputx").innerHTML = "Hello from JavaScript!";
        }
</script>

<p id="outputx">hi</p>

<button onclick="myFunction()">Click me</button>

<script>
    function myFunction() {
        document.getElementById("hellojs2").innerHTML = "Hello JavaScript!";
}
</script>

<p id="hellojs2"></p>

Lorem ipsum
===========

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

<script>
  const textList = Array.from( document.querySelectorAll("p"));
  for (var i = 0; i < textList.length; ++i) {
    textList[i].innerHTML = textList[i].innerHTML.replace(/Lorem ipsum/g,
    function replace(match) {
      return '<mark>' + match + '</mark>';
       });
       // uncomment to check that the formatting happens as expected
       //alert(textList[i].innerHTML);
  }
</script>

hi
: sdsda
