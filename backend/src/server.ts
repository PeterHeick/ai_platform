import express from 'express';
import mongoose from 'mongoose';
import passport from 'passport';
import session from 'express-session';
import bodyParser from 'body-parser';
import { Strategy as LocalStrategy } from 'passport-local';
import { User, IUser } from './models/User';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({
  origin: 'http://localhost:5173', // Din Vue3 app's URL
  credentials: true
}));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(session({ secret: 'secret', resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

// const userModel = User as UserModel;
passport.use(new LocalStrategy(User.authenticate()));

passport.serializeUser((user: Express.User, done) => {
  done(null, (user as IUser).id);
});

passport.deserializeUser(async (id, done) => {
  try {
    const user = await User.findById(id).exec();
    done(null, user);
  } catch (err) {
    done(err, null);
  }
});

// MongoDB forbindelse
mongoose.connect('mongodb://localhost:27017/ai-platform', {});

// Ruter
app.post('/register', (req, res) => {
  const { username, password } = req.body;
  User.register(new User({ username }), password, (err, user) => {
    if (err) {
      return res.status(500).send(err.message);
    }
    res.send({ message: 'User registered', user });
  });
});

// Midlertidig rute til at tømme brugersamlingen
app.post('/clear-users', async (req, res) => {
  try {
    await User.deleteMany({});
    res.send({ message: 'All users cleared' });
  } catch (err: any) {
    res.status(500).send(err.message);
  }
});

// Hent alle brugere
app.post('/users', async (req, res) => {
  try {
    const users = await User.find({}).select('+password')
    // const users = await User.find({username: /^testuser/}).select('+password')
    console.log(users);
    res.send({ message: users });
  } catch (err: any) {
    res.status(500).send(err.message);
  }
});

app.post('/login', (req, res, next) => {
  console.log('Login attempt:', req.body);
  passport.authenticate('local', (err: any, user: any, info: any) => {
    if (err) {
      console.error('Error during authentication:', err);
      return res.status(500).send('Internal Server Error');
    }
    if (!user) {
      console.warn('Authentication failed:', info);
      return res.status(401).send('Unauthorized');
    }
    req.logIn(user, (err) => {
      if (err) {
        console.error('Error during login:', err);
        return res.status(500).send('Internal Server Error');
      }
      console.log('User logged in:', user);
      return res.send({ message: 'Logget ind' });
    });
  })(req, res, next);
});

// app.post('/login', passport.authenticate('local'), (req, res) => {
//   console.log(`login request: ${JSON.stringify(req.body)}`);
//   res.status(200).send({ message: 'Logget ind' });
// });

app.listen(PORT, () => {
  console.log(`Serveren kører på http://localhost:${PORT}`);
});
