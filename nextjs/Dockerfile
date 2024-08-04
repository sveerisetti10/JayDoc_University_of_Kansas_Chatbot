# Here we are using the official Node.js 18 image
FROM node:18

# Here we set up the working directory
WORKDIR /app

# Here we copy the package.json and package-lock.json files to the working directory
COPY package*.json ./

# Here we install the dependencies
RUN npm install

# Here we copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Start the Next.js application
CMD ["npm", "run", "dev"]
