import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../services/api";

function ReviewDetails() {

  const { ticketId } = useParams();

  const navigate = useNavigate();

  const [ticket, setTicket] =
    useState(null);

  useEffect(() => {

    fetchTicket();

  }, []);

  const fetchTicket = async () => {

    try {

      const response =
        await api.get(
          `/tickets/${ticketId}`
        );

      setTicket(response.data);

    } catch (error) {

      console.error(error);
    }
  };

  const approveTicket =
    async () => {

      try {

        await api.post(
          `/reviews/${ticketId}/approve`
        );

        alert(
          "Ticket Approved"
        );

        navigate("/reviews");

      } catch (error) {

        console.error(error);
      }
    };

  const rejectTicket =
    async () => {

      try {

        await api.post(
          `/reviews/${ticketId}/reject`
        );

        alert(
          "Ticket Rejected"
        );

        navigate("/reviews");

      } catch (error) {

        console.error(error);
      }
    };

  if (!ticket) {

    return <h2>Loading...</h2>;
  }

  return (
    <div className="container mt-4">

      <div className="card shadow">

        <div className="card-header">
          <h2>
            Review Ticket
          </h2>
        </div>

        <div className="card-body">

          <h4>
            {ticket.subject}
          </h4>

          <p>
            {ticket.description}
          </p>

          <hr />

          <div className="row">

            <div className="col-md-3">
              <strong>
                Category
              </strong>
              <p>
                {ticket.category}
              </p>
            </div>

            <div className="col-md-3">
              <strong>
                Priority
              </strong>
              <p>
                {ticket.priority}
              </p>
            </div>

            <div className="col-md-3">
              <strong>
                Confidence
              </strong>
              <p>
                {ticket.confidence}
              </p>
            </div>

            <div className="col-md-3">
              <strong>
                Sentiment
              </strong>
              <p>
                {ticket.sentiment}
              </p>
            </div>

          </div>

          <hr />

          <h5>
            Draft Reply
          </h5>

          <div
            className="
            border
            rounded
            p-3
            bg-light"
          >
            {ticket.draftReply}
          </div>

          <hr />

          <h5>
            Knowledge Sources
          </h5>

          <ul>

            {
              ticket.sources?.map(
                (source) => (

                  <li key={source}>
                    {source}
                  </li>

                )
              )
            }

          </ul>

          <hr />

          <h5>
            Attachments
          </h5>

          {
            ticket.attachments
              ?.length === 0 ? (

              <p>
                No Attachments
              </p>

            ) : (

              <ul>

                {
                  ticket.attachments
                    .map(
                      (attachment) => (

                        <li
                          key={
                            attachment.fileKey
                          }
                        >
                          {
                            attachment.fileName
                          }
                        </li>

                      )
                    )
                }

              </ul>

            )
          }

          <hr />

          <div
            className="
            d-flex
            gap-3"
          >

            <button
              className="
              btn
              btn-success"
              onClick={
                approveTicket
              }
            >
              Approve
            </button>

            <button
              className="
              btn
              btn-danger"
              onClick={
                rejectTicket
              }
            >
              Reject
            </button>

          </div>

        </div>

      </div>

    </div>
  );
}

export default ReviewDetails;