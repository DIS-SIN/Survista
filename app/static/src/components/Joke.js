import React from "react"

function Joke(props){
    var question = null
    var nojoke = null
    var joke = null
    console.log(props)
    if (props.joke){
        if (props.joke.question) {
            question = <h4> question: {props.joke.question}</h4>
        }
        if (props.joke.joke){
            joke = <b> Joke: {props.joke.joke}</b>
        }
    }
    else if ( !props.joke || (joke == null && question == null)){
        nojoke = <h3> You are the joke !</h3>
    }
    return (
        <div>
          <div className = "divider"></div>
          <div className = "section">
              {question}     
              {joke}
              {nojoke}
          </div>
        </div>
    )
}

export default Joke