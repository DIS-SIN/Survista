import React from "react"

import Header from  "./components/Header"
import Jokes from "./components/Jokes";

function App(){
    return(
        <div className = "appContainer">
           <Header />
           <Jokes />
        </div>
    )
}

export default App