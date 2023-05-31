### TODO:
1. DONE Expose CarService via nginx gateway, use kompose to convert to helm chart
2. Generate helm charts for all routing services, pack them into my local kind cluster
3. Dockerize the simulation
4. Make use of CarService endpoint for random vehicle(s)
5. Run sim against RouterAPI
6. Add status updates to sim
7. Set up router to consume the queue coming from coordinates
8. Run routing on the consumed coordinates
9. Put routes back on the bus
10. Set up quick LTS consumer to store routes in a cache, provide them to FE