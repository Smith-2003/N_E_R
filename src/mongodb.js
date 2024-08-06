require('dotenv').config();
const mongoose = require("mongoose");

const mongoURI = "mongodb://localhost:27017/loginsignupDB";

if (!mongoURI) {
    throw new Error('MONGO_URI is not defined in the environment variables');
}

mongoose.connect(mongoURI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => {
        console.log("mongodb connected");
    })
    .catch((err) => {
        console.log("failed to connect", err);
    });

const LogInSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true
    },
    password: {
        type: String,
        required: true
    },
    otp: {
        type: Number,
        required: false
    }
});

const collection = new mongoose.model("collection1", LogInSchema);

module.exports = collection;
