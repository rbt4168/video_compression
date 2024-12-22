# Video Collaboration System

This project provides a collaborative video streaming system, allowing multiple users to connect, create or join rooms, invite others, and share video streams with features like mosaicking and detailed zoom-in on specific areas. The system is designed for a shared, real-time video collaboration experience.

## Features

- **Enroll Users**: Users can register their names and join the system.
- **Create and Join Rooms**: Rooms are identified by IDs (0-3) and allow collaborative sharing of video streams.
- **Invite Users**: Users can invite others to their rooms.
- **Real-Time Video Sharing**: Streams from webcams are processed to display a mosaic with specific details enhanced based on user interactions.
- **Mouse Interaction**: Users can point and interact with the video using mouse movements.

## Prerequisites

- Python 3.6+
- Required Python Libraries:
  - `opencv-python`
  - `numpy`
  - `requests`
- A working webcam.

Install dependencies using pip:
```bash
pip install opencv-python numpy requests
```

## File Overview

### Main Script
The main script handles:
- Enrolling users with a server.
- Room management (create, join, and invite operations).
- Video processing and sharing, including mosaicking and detailed zoom functionality.

### Helper Functions
1. **`mouse_callback`**: Handles mouse events for interacting with the video feed.
2. **`to_mosaic`**: Converts a video frame into a mosaic.
3. **`to_ciasom`**: Expands the mosaic back to the original video size.
4. **`merge`**: Merges the detailed region with the mosaic.
5. **`part_frame`**: Extracts and processes specific regions of the frame.

### Classes and Dependencies
- **`PERSON`**: Represents a user.
- **`DATA`**: Encapsulates video-related data.
- **`ROOM`**: Represents a room for collaboration.

These classes must be defined in the `share` module and include serialization methods (e.g., `to_dict`, `to_obj`).

## How to Use

1. Start the client:
   ```bash
   python client.py
   ```

2. Enter your unique name.
   - name should not be the same as others online
3. Choose one of the following actions:
   - **Create a Room**: Set a room ID (0-3) and start a session.
   - **Invite Users**: Invite other users by name.
   - **Search for a Room**: Search for and join an existing room.

4. Interact with the video feed:
   - Move the mouse to explore detailed areas of the mosaic.
   - Press `q` to close the video feed.

## Server Endpoint Requirements

### Endpoints
- `POST /enroll`: Enrolls a new user.
- `POST /create/{room}`: Creates a room.
- `POST /invite/{name}`: Invites a user to a room.
- `POST /search/{room}`: Searches for an existing room.
- `POST /watch/{data.ID}`: Sends and receives video data for real-time sharing.

## Known Issues
- Video stream resolution is dependent on the webcam.
- Limited to room IDs 0-3.


**Enjoy your collaborative video experience!**
