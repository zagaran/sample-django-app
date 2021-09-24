/*
 * # TODO: delete me; this is just a reference example
 */

import React from 'react';
import Hello from "../Components/Hello";

function Home(props) {
  const {message} = props;
  return (
    <div>
         <h1>You may want to wrap several components in a page, but you don't have to.</h1>
         <Hello msg={message}/>
       </div>
  );
}

export default Home;
