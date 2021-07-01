import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import axios from 'axios'
import './App.css';

function App() {
  let [petInfo, setPetInfo] = useState<any>({})

  useEffect(() => {
    getPetInformation()
  }, [])

  
  async function getPetInformation() {
    let petInformation = await axios.get("https://iy3vvzrq1i.execute-api.us-east-1.amazonaws.com/prod/animal/678910")
    setPetInfo(petInformation)
    console.log(petInformation)
  }
  async function adopt() {
    console.log("Adopted")
  }

  return (

    
    <body>

      <h1>Husky Center Pet of the month</h1>
      <table>
      <tr>
        <table>
          <tr>
            <th>{petInfo.data.IMG_1}</th>
            <th>{petInfo.data.IMG_2}</th>
          </tr>
            <th>{petInfo.data.IMG_3}</th>
            <th>{petInfo.data.IMG_4}</th>
        </table>
      </tr>
      <tr>
      <table>
          <tr>
            <th>Nombre</th>
            <th>Ubicacion</th>
            <th>Edad</th>
            <th>Estado de Salud</th>
          </tr>
            <td>{petInfo.data.nombre}</td>
            <td>{petInfo.data.ubicacion}</td>
            <td>{petInfo.data.edad}</td>
            <td>{petInfo.data.estado_de_salud}</td>
        </table>
        </tr>
      </table>

<div id="wrapper">    
    <div className="boton"
        onClick={adopt} >Your text</div>
</div>
    </body>
  );
}

export default App;

