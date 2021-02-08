import React, {Component} from 'react';
import Hello from "../Components/Hello";

class Home extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <div>
        <h1>You may want to wrap several components in a page, but you don't have to.</h1>
        <Hello msg={this.props.message}/>
      </div>
    );
  }
}

export default Home;