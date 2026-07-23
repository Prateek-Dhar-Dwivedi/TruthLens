import { useEffect,useState } from "react";
import api from "../api";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";

import {
  FaCheckCircle,
  FaTimesCircle,
  FaQuestionCircle,
  FaSearch
} from "react-icons/fa";

import "./Dashboard.css";

const COLORS=["#14B8A6","#EF4444","#F59E0B"];

function Dashboard(){

  const [stats,setStats]=useState(null);
  const [history,setHistory]=useState([]);
  const [loggedIn,setLoggedIn]=useState(false);
  const [loading,setLoading]=useState(true);

  useEffect(()=>{

    const token=localStorage.getItem("token");

    if(token){
      setLoggedIn(true);
      loadData();
    }
    else{
      setLoggedIn(false);
      setLoading(false);
    }

  },[]);


  const loadData=async()=>{

    try{

      const token=localStorage.getItem("token");

      const config={
        headers:{
          Authorization:token
        }
      };

      const statsRes=await api.get("/stats",config);
      const historyRes=await api.get("/history",config);

      setStats(statsRes.data);
      setHistory(historyRes.data.slice(0,5));

    }
    catch(err){

      console.log(err);

      localStorage.removeItem("token");
      setLoggedIn(false);

    }
    finally{
      setLoading(false);
    }

  };


  if(loading){

    return(
      <div className="loading">
        Loading Dashboard...
      </div>
    );

  }


  if(!loggedIn){

    return(
      <div className="loading">

        <h2>
          Login First
        </h2>

        <p>
          Please login to view your dashboard analytics.
        </p>

      </div>
    );

  }


  if(!stats){

    return(
      <div className="loading">
        No Dashboard Data Found
      </div>
    );

  }


  const pieData=[
    {name:"True",value:stats.true_claims},
    {name:"False",value:stats.false_claims},
    {name:"Uncertain",value:stats.uncertain_claims}
  ];


  const areaData=[
    {name:"Checks",value:stats.total_checks},
    {name:"True",value:stats.true_claims},
    {name:"False",value:stats.false_claims},
    {name:"Uncertain",value:stats.uncertain_claims}
  ];


  return(
    <div className="dashboard">

      <h1>TruthLens Analytics</h1>

      <div className="stats-grid">

        <div className="stat-card">
          <FaSearch className="stat-icon"/>
          <h3>Total Checks</h3>
          <h2>{stats.total_checks}</h2>
        </div>

        <div className="stat-card">
          <FaCheckCircle className="stat-icon success"/>
          <h3>True Claims</h3>
          <h2>{stats.true_claims}</h2>
        </div>

        <div className="stat-card">
          <FaTimesCircle className="stat-icon danger"/>
          <h3>False Claims</h3>
          <h2>{stats.false_claims}</h2>
        </div>

        <div className="stat-card">
          <FaQuestionCircle className="stat-icon warning"/>
          <h3>Uncertain</h3>
          <h2>{stats.uncertain_claims}</h2>
        </div>

      </div>

      <div className="charts-grid">

        <div className="chart-card">

          <h3>Verdict Distribution</h3>

          <ResponsiveContainer width="100%" height={350}>

            <PieChart>

              <Pie
                data={pieData}
                dataKey="value"
                outerRadius={120}
                label
              >
                {
                  pieData.map((item,index)=>(
                    <Cell
                      key={index}
                      fill={COLORS[index]}
                    />
                  ))
                }
              </Pie>

              <Tooltip/>
              <Legend/>

            </PieChart>

          </ResponsiveContainer>

        </div>


        <div className="chart-card">

          <h3>Platform Statistics</h3>

          <ResponsiveContainer width="100%" height={350}>

            <AreaChart data={areaData}>

              <CartesianGrid strokeDasharray="3 3"/>

              <XAxis dataKey="name"/>

              <YAxis/>

              <Tooltip/>

              <Area
                type="monotone"
                dataKey="value"
                stroke="#14B8A6"
                fill="#14B8A6"
              />

            </AreaChart>

          </ResponsiveContainer>

        </div>

      </div>


      <div className="history-card">

        <h3>Recent Fact Checks</h3>

        <table>

          <thead>
            <tr>
              <th>Claim</th>
              <th>Verdict</th>
              <th>Confidence</th>
            </tr>
          </thead>

          <tbody>

            {
              history.map((item,index)=>(
                <tr key={index}>
                  <td>{item.claim}</td>
                  <td>{item.verdict}</td>
                  <td>{item.confidence}%</td>
                </tr>
              ))
            }

          </tbody>

        </table>

      </div>

    </div>
  );

}

export default Dashboard;