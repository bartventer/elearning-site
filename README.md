<!-- markdownlint-disable -->
# E-learning application
This is an e-learning platform developed with Django. It includes a content management system (CMS) that instructors can use to create their own contents. Students can register and enrol to courses. Finally, each course has it's own chatroom in which enrolled users can communicate through a web-socket connection.

# Features

- Custom groups and permissions
- Content management system (CMS), with AJAX-based drag-and-drop functionality for ordering contents
- Memecached cache back end; content is cached and returned for all GET requests 
- RESTful API that can be consumed by any other application ([follow the link](https://github.com/bartventer/elearning-site/tree/master/educa/courses/api)).
- Chat server using RedisChannels:
	- WebSocket consumer and client
	- Redis channel layer used to enable communication between consumers
	- Fully asynchronous consumer
- PostgreSQL database
- Web server with uWSGI and Nginx
- Channels served through Daphne to support WebSockets for the chat server
# Installation and set-up
Download/clone/fork the repository and install the `requirements.txt` file in your virtual environment.

### Production set-up
The production site was run on an AWS EC2 instance, through Nginx, uWSGI and Daphne. For ease of reference I've included a sample of the Nginx [configuration file](https://github.com/bartventer/elearning-site/tree/master/educa/config) that was used on the Linux Ubuntu 18.04 virtual machine.

Linux installation:

    $ sudo apt-get update
    $ sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib python3-venv libevent-dev
    
Additionally, you'll need to install and configure Redis, Memecache and PostgreSQL. Follow the instructions on the respective websites for guidance on installation.



# Application Flow
## Instructors

Instructors have access to a CMS, and can create their own courses, add modules to those courses and create content for each module (text, image, video, file).

Different permission groups exist on the admin site. The user must first be added to the instructors group in order to receive the necessary permission to access the CMS.

### Admin site:
First, some subjects need to be created.
![enter image description here](https://github.com/bartventer/elearning-site/blob/master/educa/media/4.%20127.0.0.1_8000_admin_courses_subject_.png?raw=true)

 Creating the instructors group and assigning read & write permission for courses, modules and contents.

- Instructors group permissions
![enter image description here](https://github.com/bartventer/elearning-site/blob/master/educa/media/1.%20127.0.0.1_8000_admin_auth_group_.png?raw=true)
![enter image description here](https://github.com/bartventer/elearning-site/blob/master/educa/media/2.%20127.0.0.1_8000_admin_auth_group_1_change_.png?raw=true)
- Assign instructor permission to a user
![enter image description here](https://github.com/bartventer/elearning-site/blob/master/educa/media/3.%20127.0.0.1_8000_admin_auth_group_1_change_.png?raw=true)


### CMS site:
Creating content as an instructor is done at the following uri: ''http://domain_name/course/mine/''

1. Create a new course
![enter image description here](https://github.com/bartventer/elearning-site/blob/master/educa/media/5.%20127.0.0.1_8000_course_mine_.png?raw=true)
![enter image description here](https://github.com/bartventer/elearning-site/blob/master/educa/media/6.%20127.0.0.1_8000_course_create_.png/?raw=true)

2. Create course modules
![](https://github.com/bartventer/elearning-site/blob/master/educa/media/7.%20127.0.0.1_8000_course_mine_.png?raw=true)

![](https://github.com/bartventer/elearning-site/blob/master/educa/media/8.%20127.0.0.1_8000_course_7_module_.png?raw=true)
3. Add contents to modules (text, image, video, file). 
![](https://github.com/bartventer/elearning-site/blob/master/educa/media/9.%20127.0.0.1_8000_course_module_13.png?raw=true)
![](https://github.com/bartventer/elearning-site/blob/master/educa/media/10.%20127.0.0.1_8000_course_module_13_content_video_create_.png?raw=true)
4. Modules and module contents can be re-arranged via the AJAX-based drag-and-drop functionality.
	![](https://github.com/bartventer/elearning-site/blob/master/educa/media/11.%20127.0.0.1_8000_course_module_13_content_video_create_.png?raw=true)

## Students

### Home page: 
Students are able to browse through the various courses. If they want to access the content they must enrol with a registered account. 
![](https://github.com/bartventer/elearning-site/blob/master/educa/media/12.%20127.0.0.1_8000_%20homepage.png?raw=true)

### Enrol in a course:
- Enrolment
![](https://github.com/bartventer/elearning-site/blob/master/educa/media/13.%20127.0.0.1_8000_course_advanceddjango.png?raw=true)
- Registered account required
![](https://github.com/bartventer/elearning-site/blob/master/educa/media/14.%20127.0.0.1_8000_students_register_.png?raw=true)

### Enrolled course access:

- Access to all content
![](https://github.com/bartventer/elearning-site/blob/master/educa/media/15.%20127.0.0.1_8000_students_course_7_.png?raw=true)

## Chatroom
Each course has its own chatroom WebSocket. Enrolled students and instructors are able to join.

- Establishing the connection. Standard TCP socket used by server to listen for incoming socket connections. Below is the handshake to bridge from HTTP to WebSockets.
![enter image description here](https://github.com/bartventer/elearning-site/blob/master/educa/media/16%20websocket%20protocol%20and%20connection%20upgrade_2.png?raw=true)

- Fully asynchronous
![](https://github.com/bartventer/elearning-site/blob/master/educa/media/17%20chatroom.png?raw=true)
- Example of the stateful WebSocket connection that is persisted; on the right a connection was terminated and restarted and on the left a different connection was persisted throughout, this can be evidenced through the chat history (reset on right, but persisted on left).
![](https://github.com/bartventer/elearning-site/blob/master/educa/media/18%20User%20connection%20lost.png?raw=true)


