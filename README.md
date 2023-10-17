# Fast API - Fetch Screenshots

## Vanilla Installation

### FastAPI
In folder /fastapi/ a standard Python + FastAPI installation would be:
```
virtualenv --python=python3.10 venv
source venv/bin/activate
pip install fastapi uvicorn databases databases[sqlite] sqlmodel
```

### Node JS
In folder /nodejs/ a standard Node.JS installation would be:
```
npm install puppeteer
```

## Vanilla Running

In folder /fastapi/ either:
```
uvicorn app:app --reload --host 127.0.0.1 # On local machine
uvicorn app:app --reload --host 0.0.0.0 # On separate/dedicated machine
```

## Docker + Docker Compose Installation
```
To be defined
```

## Docker + Docker Compose Running
```
To be defined
```

## API Tests

### Check Server Is Alive

`GET http://localhost:8000/isalive`  
**content-type:** application/json

### Initiate Fetch Screenshots Process

`POST http://localhost:8000/screenshots`  
**content-type:** application/json

```
{
    "start_url": "https://www.website-here.com/",
    "number_of_links": 3
}
```

### Fetch Single Screenshot

`GET http://localhost:8000/screenshots/UUID_HERE`  
**content-type:** application/json


## Performance Considerations

Even though Puppeteer and Playwright support similar APIs, Puppeteer seems to have a sizeable speed advantage. Puppeteer and Playwright scripts show faster execution time (close to 20% in E2E scenarios) compared to the Selenium and DevTools WebDriverIO flavours.

So, long story short:  
I chose Puppeteer, as it seems it is the fastest headless browser library.


## Focus Points:

### 1. Performance optimizations of the service

The Python and Javascript services should be fully decoupled.
The current implementation will combine the Python & JS services into a single Docker Compose.

But in a real world application I will split those into 2 fully separate services (and repos), so they can be independently scalable.
More specifically, the JS Service that generates the screenshots should be horizontally scalable.
While the Python Service should be responsible for the orchestration.

### 2. How storing web page screenshots could be optimised, if we’re going to expect high usage ?

For now I have done the most basic optimization - by changing the image type of the screenshots from .png to .jpg.
But in a real world application I can do a much more detailed research.

A quick Google Search led me to the following pages:
https://www.bannerbear.com/blog/ways-to-speed-up-puppeteer-screenshots/
https://stackoverflow.com/questions/67291945/reduce-size-of-headless-puppeteer-screenshot
So there is a lot more that can be done.

### 3. How monitoring could be implemented and what is important to be monitored.
Actually, there are a lot of things that can be done for monitoring:

- Logging
We can add comprehensive logging to capture relevant information, including errors, warnings, and information about application behavior. With structured log formats to make it easier to analyze and search logs.

- Error Tracking
Integrate error tracking tools like Sentry (recommended), Rollbar, or New Relic to capture and notify for errors in real-time.
For both Python-based Services and Node.JS-based services - Sentry works great.

- Performance Metrics
Collect and monitor performance metrics, such as response times, request rates, and resource utilization (CPU, memory).
By using tools like Prometheus, Grafana, or Datadog we can create dashboards and set up alerts for performance anomalies.

- Screenshot Storage
We may have to monitor the storage space used for storing screenshots.
We can set up alerts to be notified when storage reaches predefined thresholds.

- And more:
Resource Utilization / Container Orchestration Monitoring / Alerting / API Monitoring / etc...

### 4. Bonus points for service to be able to run inside docker

To be added.

## Further Improvements

Here is just a quick short list of things that can be further improved:

- [ ] Finish the **Docker + Docker Compose** configuration

- [ ] Split the functionality (Python / Node.JS) into 2 different repos  
These can be maintained separately.

- [ ] Add tests  
At this phase an Integration or even End-to-End test may bring more value as we don't have lots of testable units.

- [ ] Prepare Flowchart diagrams  
Either in Mermaid or Miro Board.

- [ ] Double check that we don't have any blocking code  
Within the async functionalities of both services

- [ ] Setup **Terraform** and **K8S**  
So we can test this in a more real-world enviornment

- [ ] Make the functionality elastic  
Based on the number of links to Crawl we should spawn less-or-more Crawling processes.

- [ ] Add configuration capabilities  
For example, whether the Crawlers should prioritize **BFS** or **DFS**.

- [ ] Replace the **Node.JS Puppeteer-based service** with **Rust Headless Chrome**:  
https://github.com/rust-headless-chrome/rust-headless-chrome  
_There is a chance we can extract significantly better performance here. This has to be tested in an isolated enviornment before approaching this as a separate project._

- _And more ..._