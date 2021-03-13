window.onload = function(){
    const spans = document.getElementsByTagName("span");
    const spans_content = document.getElementsByClassName("span_content")[0].getElementsByTagName("div")
    let current_tab_index = 0
    for (let i = 0; i < spans.length; i++) {
        spans[i].index = i;
        spans[i].onclick = function (){
            for (let j = 0; j < spans.length; j++) {
                spans[j].className = "";
                spans_content[j].className = "";
            }
            current_tab_index = i
            this.className = "select_color";
            spans_content[this.index].className = "display";
        }
        spans[i].onmouseenter = function (){
            this.className = "select_color";
        }
        spans[i].onmouseleave = function (){
            if (this.index !== current_tab_index){
                this.className = ""
            }
        }
    }
}