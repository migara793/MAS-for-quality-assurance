#!/bin/bash

set -e

echo "Running unit tests..."
npm install
npm test

echo "Unit tests completed."
