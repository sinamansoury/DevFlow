import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'

import Sidebar from '../components/Sidebar'
function Projects() {

  const [projects, setProjects] = useState([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)


  const loadProjects = async () => {

    try {

      setLoading(true)
      setError('')


      const response = await api.get(
        `/projects/?page=${page}`
      )


      setProjects(
        response.data.results ||
        response.data
      )


      if (response.data.count) {

        setTotalPages(
          Math.ceil(
            response.data.count / 10
          )
        )

      } else {

        setTotalPages(1)

      }


    } catch (err) {

      console.error(err)

      setError(
        'دریافت پروژه‌ها انجام نشد.'
      )


    } finally {

      setLoading(false)

    }

  }


  useEffect(() => {

    loadProjects()

  }, [page])



  if (loading) {

    return (

      <div
        className="dashboard"
        dir="rtl"
      >

        <main className="main-content">

          <div className="dashboard-card">

            <div className="empty-state">

              <div className="empty-icon">
                ⏳
              </div>

              <p>
                در حال دریافت پروژه‌ها...
              </p>

            </div>

          </div>

        </main>

      </div>

    )

  }



  return (

    <div
      className="dashboard"
      dir="rtl"
    >


      <Sidebar />



      <main className="main-content">


        <div className="topbar">


          <div>

            <div
              style={{
                color:'#64748b',
                fontSize:'13px',
                marginBottom:'8px'
              }}
            >
              Projects
            </div>


            <h1>
              پروژه‌ها
            </h1>


            <p>
              مدیریت تمام پروژه‌هایی که به آن‌ها دسترسی دارید.
            </p>


          </div>


        </div>



        {error && (

          <div className="auth-error">

            {error}

          </div>

        )}



        <div className="dashboard-card">


          <div className="card-header">


            <div>

              <h3>
                لیست پروژه‌ها
              </h3>


              <p
                style={{
                  color:'#64748b',
                  fontSize:'12px',
                  marginTop:'5px'
                }}
              >
                پروژه‌های Workspaceهای شما
              </p>


            </div>


          </div>
                {projects.length === 0 ? (

            <div className="empty-state">

              <div className="empty-icon">
                ◫
              </div>

              <strong>
                پروژه‌ای وجود ندارد
              </strong>

              <p>
                هنوز پروژه‌ای برای شما ثبت نشده است.
              </p>

            </div>


          ) : (


            <>

              <div
                style={{
                  display:'grid',
                  gridTemplateColumns:
                    'repeat(auto-fill, minmax(280px, 1fr))',
                  gap:'16px',
                }}
              >


                {projects.map((project) => (

                  <Link
                    key={project.id}
                    to={`/projects/${project.id}`}
                    className="stat-card"
                    style={{
                      textDecoration:'none',
                      color:'inherit',
                      display:'block',
                      cursor:'pointer',
                    }}
                  >


                    <div
                      style={{
                        display:'flex',
                        alignItems:'center',
                        gap:'12px',
                        marginBottom:'15px',
                      }}
                    >

                      <div
                        style={{
                          width:'42px',
                          height:'42px',
                          borderRadius:'12px',
                          display:'flex',
                          alignItems:'center',
                          justifyContent:'center',
                          background:
                            'rgba(99,102,241,0.12)',
                          color:'#818cf8',
                        }}
                      >
                        ◫
                      </div>


                      <div>

                        <strong>
                          {project.name}
                        </strong>


                        <div
                          style={{
                            color:'#475569',
                            fontSize:'11px',
                            marginTop:'5px',
                          }}
                        >

                          Workspace:
                          {' '}

                          {project.workspace_name ||
                            `#${project.workspace}`}

                        </div>


                      </div>


                    </div>



                    <p
                      style={{
                        color:'#64748b',
                        fontSize:'13px',
                        lineHeight:'1.8',
                        minHeight:'46px',
                      }}
                    >

                      {project.description ||
                        'بدون توضیحات'}

                    </p>



                    <div
                      style={{
                        marginTop:'16px',
                        paddingTop:'13px',
                        borderTop:
                          '1px solid #1e293b',
                      }}
                    >

                      <span
                        style={{
                          color:'#818cf8',
                          fontSize:'12px',
                        }}
                      >
                        مشاهده پروژه ←
                      </span>


                    </div>


                  </Link>

                ))}


              </div>



              {totalPages > 1 && (
  <div
    style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      gap: '7px',
      marginTop: '28px',
      paddingTop: '22px',
      borderTop: '1px solid #1e293b',
    }}
  >

    {/* قبلی */}
    <button
      type="button"
      disabled={page === 1}
      onClick={() =>
        setPage((p) => p - 1)
      }
      style={{
        height: '36px',
        minWidth: '68px',
        padding: '0 12px',
        border: '1px solid #263247',
        borderRadius: '9px',
        background: '#111827',
        color:
          page === 1
            ? '#475569'
            : '#94a3b8',
        fontFamily: 'inherit',
        fontSize: '12px',
        cursor:
          page === 1
            ? 'not-allowed'
            : 'pointer',
        opacity:
          page === 1 ? 0.5 : 1,
      }}
    >
      ← قبلی
    </button>


    {/* شماره صفحات */}
    {Array.from(
      {
        length: totalPages,
      },
      (_, index) => index + 1
    ).map((item) => {

      const active = item === page

      return (
        <button
          type="button"
          key={item}
          onClick={() =>
            setPage(item)
          }
          style={{
            width: '36px',
            height: '36px',
            padding: 0,
            border: active
              ? '1px solid #6366f1'
              : '1px solid #263247',
            borderRadius: '9px',
            background: active
              ? '#6366f1'
              : '#111827',
            color: active
              ? '#ffffff'
              : '#94a3b8',
            fontFamily: 'inherit',
            fontSize: '12px',
            fontWeight: active
              ? '600'
              : '400',
            cursor: 'pointer',
            boxShadow: active
              ? '0 4px 12px rgba(99, 102, 241, 0.2)'
              : 'none',
            transition: 'all 0.2s ease',
          }}
        >
          {item}
        </button>
      )
    })}


    {/* بعدی */}
    <button
      type="button"
      disabled={
        page === totalPages
      }
      onClick={() =>
        setPage((p) => p + 1)
      }
      style={{
        height: '36px',
        minWidth: '68px',
        padding: '0 12px',
        border: '1px solid #263247',
        borderRadius: '9px',
        background: '#111827',
        color:
          page === totalPages
            ? '#475569'
            : '#94a3b8',
        fontFamily: 'inherit',
        fontSize: '12px',
        cursor:
          page === totalPages
            ? 'not-allowed'
            : 'pointer',
        opacity:
          page === totalPages
            ? 0.5
            : 1,
      }}
    >
      بعدی →
    </button>

  </div>
)}


            </>

          )}


        </div>


      </main>


    </div>

  )

}


export default Projects