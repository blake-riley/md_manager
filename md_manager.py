import web
import views


urls = (
	'/', 'index',
	'/jobs', 'jobs',
	'/simulations', 'sims',
	'/new', 'new'
)


class index:
	def GET(self):

		index_content = """<div class="hero-unit">
        <h1>Welcome!</h1><br>
        <p>MD manager is a small and lightweight web interface for automated setup, running and analysis of molecular dynamics simulations.</p>
        </div>"""

		render = web.template.render('templates/')
		return render.index(index_content)


class jobs:
	def GET(self):

		job_content = views.get_jobs()
		render = web.template.render('templates/')
		return render.index(job_content)

class sims:
	def GET(self):
		sim_content = views.get_sims()
		render = web.template.render('templates/')
		return render.index(sim_content)

class new:
	def GET(self):
		render = web.template.render('templates/')
		return render.index("This will be a simulation setup wizard, one day...")






if __name__ == "__main__":
	app = web.application(urls, globals())
	app.run()