# Deployment
[ ] Get the code to show after generating a video (everytime user hits enter, not just the first time)
[ ] figure out why its taking so long to run for an average small query - theres probably a blog post about llm latency in there


# TODO
[ ] make sure we are using manim or manimgl in the function calls deliberately
[ ] change default quality to low
[ ] think about encouraging the model to create functions, mobjects, and scenes
[ ] fix requirements.txt with either manim or manimgl environment that works on ubuntu
[ ] get enter to start generating content instead of clicking button 
[ ] if we do use manimgl, come up with a list of footguns / things that have changed and figure out how to work them into the system prompt

how do i set up llama.cpp to run locally?

What is the best model to use? codestral-25.01
- how important is token length? what is the expected token length of a program? 1000 lines of code, 1000 words max
    - maybe even longer if we want to add in context pairs. 
how hard is it to get llama.cpp running on a server, and how much would it cost?

where are we injecting the prompt again? do some prompt engineering to figure out the most useful thing to prepend to the user input 

figure out how to cache and group inputs. many people are going to want to see the same things, and we should be able to compose videos about these better if we are able to cache the subcomponents (both performance and determinism wise. bobviously we dont get determinism entirely but its reducing the degrees of freedom for a video on the fast fourier transform when we already have a great visualization on the regular fourier transform x)


# Testing and Validation
Strategy for testing the endpoints:
```
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a circle that transforms into a square",
    "options": {
      "quality": "low",
      "resolution": "720p"
    }
  }'
```
should give
```
{
  "task_id": "some-uuid",
  "status": "pending"
}
```

`curl http://localhost:8000/status/your-task-id-here`
should give 
```
response = {
  "task_id": "your-task-id-here",
  "status": "completed",
  "code": "from manim import *\n...",
  "video_url": "/videos/task-id/animation.mp4",
  "error": null
}
```

`curl http://localhost:8000/videos/task-id/animation.mp4 --output animation.mp4`    


TODO try distilling 
Try fine tuning, RLHF'ing on some open source math datasets

https://huggingface.co/datasets/open-r1/OpenR1-Math-220k

TODO turn the 3blue1brown videos into a dataset for the model to train on.
- what format should the dataset be
- do we want to try to train a reasoning model?
- could we do our own distillation of a bigger model and mix in heavier samples of the 3b1b videos? 

Add some buttons with default inputs so people can try it out without having to type anything in.
- cache these videos so we don't have to regenerate them every time.

Add flake8 and code formatting to the generated code as part of the validation/sanitization 

automatically save events when the code doesn't run

# Deployment
add DROPLET_IP, DROPLET_USER, and SSH_PRIVATE_KEY to the GH repo environment variables
on the droplet, run 
```
git clone your-repo
cd your-repo
docker-compose up -d
```

Set up Nginx as reverse proxy
`sudo apt install nginx`


# Potential Data Sources
https://themanimrepository.wordpress.com/
https://docs.manim.community/en/stable/examples.html