import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import axios from 'axios'
import './App.css';

function App() {
  let [Nombre, setNombre] = useState<any>({})
  let [ApellidoMaterno, setApellidoMaterno] = useState<any>({})
  let [ApellidoPaterno, setApellidoPaterno] = useState<any>({})
  let [Edad, setEdad] = useState<any>({})
  let [Email, setEmail] = useState<any>({})
  let [Direccion, setDireccion] = useState<any>({})
  let [HouseType, setHouseType] = useState<any>({})



  let [petInfo, setPetInfo] = useState<any>({})


  async function handleNombre(event:any){
    setNombre(event.target.value)
  }

  async function handleAM(event:any){
    setApellidoMaterno(event.target.value)
  }

  async function handleAP(event:any){
    setApellidoPaterno(event.target.value)
  }

  async function handleEdad(event:any){
    setEdad(event.target.value)
  }

  async function handleUbicacion(event:any){
    setDireccion(event.target.value)
  }

  async function handleEmail(event:any){
    setEmail(event.target.value)
  }

  async function handleTipoCasa(event:any){
    setHouseType(event.target.value)
  }

  async function handleThis(event:any){
    setAdopterInfo()
  }

  useEffect(() => {
    getPetInformation()
  }, [])

  
  async function getPetInformation() {
    let petInformation = await axios.get("https://iy3vvzrq1i.execute-api.us-east-1.amazonaws.com/prod/animal/678910")
    setPetInfo(petInformation)
    console.log(petInformation)
    
  }

  async function setAdopterInfo() {
    let Adoptinformation = await axios.put("https://iy3vvzrq1i.execute-api.us-east-1.amazonaws.com/prod/adopter/123459",{nombre: Nombre,apellido_materno:ApellidoMaterno,apellido_paterno:ApellidoPaterno,edad:Edad,email:Email,ubicacion:Direccion})
    setAdopterAndDog()
  }

  async function setAdopterAndDog() {
    let petInformation = await axios.put("https://iy3vvzrq1i.execute-api.us-east-1.amazonaws.com/prod/adopter/123459/animal/678910",{house_type: HouseType})
    console.log(petInformation)
  }



  async function adopt() {
    console.log("Adopted")
  }



  return (
    <body>
      <h1>Husky Center Pet of the month</h1>
      {petInfo.data!=null && 
      <table>
      <tr>
        <table>
          <tr>
            <th>
              <img src={petInfo.data.IMG_1}></img></th>
            <th><img src={petInfo.data.IMG_2}></img></th>
          </tr>
            <th><img src={petInfo.data.IMG_3}></img></th>
            <th><img src={petInfo.data.IMG_4}></img></th>
        </table>
      </tr>
      <tr>
      <table>
          <tr>
            <th>Nombre</th>
            <th>Codigo</th>
            <th>Ubicacion</th>
            <th>Edad</th>
            <th>Estado de Salud</th>
          </tr>
            <td>{petInfo.data.nombre}</td>
            <td>{petInfo.data.pk}</td>
            <td>{petInfo.data.ubicacion}</td>
            <td>{petInfo.data.edad}</td>
            <td>{petInfo.data.estado_de_salud}</td>
        </table>
        </tr>
      </table>
      }

<div id="wrapper">    
<form onSubmit={handleThis}>
  <label>
    Nombre:
    <input type="text" value={Nombre} name="Nombre" onChange={handleNombre}/>
  </label>
  <label>
    Apellido materno:
    <input type="text" value={ApellidoMaterno} name="Apellido materno" onChange={handleAM}/>
  </label>
  <label>
    Apellido paterno:
    <input type="text" value={ApellidoPaterno} name="Apellido paterno" onChange={handleAP}/>
  </label>
  <label>
    Edad:
    <input type="text" value={Edad} name="Edad" onChange={handleEdad}/>
  </label>
  <label>
    Ubicacion:
    <input type="text" value={Direccion} name="Ubicacion" onChange={handleUbicacion}/>
  </label>
  <label>
    Email:
    <input type="text" value={Email} name="Email" onChange={handleEmail}/>
  </label>
  <label>
    Tipo De Casa:
    <input type="text" value={HouseType} name="Tipo De Casa" onChange={handleTipoCasa}/>
  </label>

  <input type="submit" value="Mandar Solicitud"/>
</form>
</div>

    </body>
  );
}



export default App;

